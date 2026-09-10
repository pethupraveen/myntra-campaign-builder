"""Pull a day of ad-group performance out of the Myntra ads portal into the daily log.

The portal has no public API and no service credential: the report tab is an XHR made by the
page itself, authenticated by the seller session cookie. So the request is not written here,
it is captured once from the browser (DevTools > Network > the report call > Copy as cURL)
and replayed with the date swapped. Re-capture when the session expires.

    python src/fetch_daily.py --date 2026-09-09
    python src/fetch_daily.py --date 2026-09-09 --dry-run   # show the request, send nothing
    python src/fetch_daily.py --date 2026-09-09 --inspect   # dump the response shape

Writes data/daily_log.csv (one row per group per day, upserted by Date+AG). The workbook is a
separate step - src/Write-DailyTracker.ps1 reads that CSV over Excel COM.
"""
import argparse, csv, datetime as dt, json, pathlib, re, shlex, sys

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CURL = ROOT / 'secrets' / 'myntra_curl.txt'
FIELDS = ROOT / 'config' / 'myntra_fields.json'
GROUPMAP = ROOT / 'config' / 'adgroup_map.json'
OUT = ROOT / 'data' / 'daily_log.csv'
HEAD = ['Date', 'AG', 'Group', 'Spend', 'Impressions', 'Clicks', 'Orders', 'GrossRev']

# The metric a portal column carries, by the key names Myntra has used for it. Matching is on
# the key with non-letters stripped, so adGroupName / ad_group_name / AdGroupName all collapse
# to one candidate. Order matters: the first hit in a row's keys wins.
CANDIDATES = {
    'group':       ['adgroupname', 'adgroup', 'groupname', 'adgroupid', 'name'],
    'spend':       ['spend', 'cost', 'totalcost', 'amountspent', 'budgetspent', 'totalspend'],
    'impressions': ['impressions', 'impression', 'totalimpressions', 'views'],
    'clicks':      ['clicks', 'click', 'totalclicks'],
    'orders':      ['orders', 'totalorders', 'conversions', 'units', 'unitssold', 'quantity'],
    'revenue':     ['revenue', 'totalrevenue', 'gmv', 'sales', 'directrevenue', 'revenuegenerated'],
}


# ---------------------------------------------------------------- the captured request
def parse_curl(text):
    """A DevTools 'Copy as cURL' line -> method, url, headers, body."""
    text = re.sub(r'\\\r?\n', ' ', text.strip())          # unfold bash line continuations
    text = re.sub(r'\^\r?\n', ' ', text)                  # ... and cmd.exe ones
    argv = shlex.split(text)
    if argv and argv[0] == 'curl':
        argv = argv[1:]
    url, method, body, headers = None, None, None, {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ('-H', '--header'):
            i += 1
            k, _, v = argv[i].partition(':')
            headers[k.strip()] = v.strip()
        elif a in ('-b', '--cookie'):
            i += 1
            headers['Cookie'] = argv[i]
        elif a in ('-d', '--data', '--data-raw', '--data-binary', '--data-ascii'):
            i += 1
            body = argv[i]
        elif a in ('-X', '--request'):
            i += 1
            method = argv[i]
        elif a.startswith('-'):
            pass                                          # --compressed, --insecure, -s, ...
        elif url is None:
            url = a
        i += 1
    if not url:
        sys.exit('No URL in the cURL capture. Re-copy the report request from DevTools.')
    return method or ('POST' if body else 'GET'), url, headers, body


# ---------------------------------------------------------------- date substitution
ISO = re.compile(r'\d{4}-\d{2}-\d{2}')
DMY = re.compile(r'\b(\d{2})-(\d{2})-(\d{4})\b')
EPOCH_MS = re.compile(r'\b1[5-9]\d{11}\b')                # 2017-2033 in milliseconds


def retarget(s, day):
    """Rewrite every date the capture carried to `day`. Returns (text, [what changed])."""
    if not s:
        return s, []
    changed = []

    def swap(new):
        def f(m):
            if m.group(0) != new:
                changed.append(m.group(0) + ' -> ' + new)
            return new
        return f

    s = ISO.sub(swap(day.isoformat()), s)
    s = DMY.sub(swap(day.strftime('%d-%m-%Y')), s)

    # An epoch stamp is one end of the range. Move it to the target day keeping its exact
    # time of day, so a 00:00:00 start stays a start and a 23:59:59 end stays an end - a
    # start/end guess would collapse both onto the same instant and ask for a zero-width range.
    def ep(m):
        old = dt.datetime.fromtimestamp(int(m.group(0)) / 1000)
        new = int(dt.datetime.combine(day, old.time()).timestamp() * 1000)
        if str(new) != m.group(0):
            changed.append('{} -> {} ({:%H:%M:%S} kept)'.format(m.group(0), new, old))
        return str(new)

    s = EPOCH_MS.sub(ep, s)
    return s, changed


# ---------------------------------------------------------------- response -> rows
def deepest_rows(obj):
    """The longest list-of-dicts anywhere in the response: the report table."""
    best = []

    def walk(o):
        nonlocal best
        if isinstance(o, list):
            if o and all(isinstance(x, dict) for x in o) and len(o) > len(best):
                best = o
            for x in o:
                walk(x)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)

    walk(obj)
    return best


def flatten(row, prefix=''):
    """One level of nesting is common (row.metrics.clicks); flatten so key matching sees it."""
    out = {}
    for k, v in row.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + '.'))
        else:
            out[prefix + k] = v
    return out


def norm(k):
    return re.sub(r'[^a-z]', '', k.lower())


def resolve_fields(row, override):
    """metric -> the key in `row` that holds it."""
    keys = {norm(k): k for k in row}
    picked = {}
    for metric, names in CANDIDATES.items():
        if metric in override:
            picked[metric] = override[metric]
            continue
        for n in names:
            for nk, real in keys.items():
                if nk == n or nk.endswith(n):
                    picked[metric] = real
                    break
            if metric in picked:
                break
    return picked


def number(v):
    if v is None or v == '':
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    v = re.sub(r'[^\d.\-]', '', str(v))                   # strips Rs, commas, %
    return float(v) if v not in ('', '-', '.') else 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--date', default=(dt.date.today() - dt.timedelta(days=1)).isoformat(),
                   help='day to fetch, YYYY-MM-DD (default: yesterday)')
    p.add_argument('--curl', type=pathlib.Path, default=CURL)
    p.add_argument('--out', type=pathlib.Path, default=OUT)
    p.add_argument('--dry-run', action='store_true',
                   help='print the retargeted request, send nothing')
    p.add_argument('--inspect', action='store_true',
                   help='send, then dump the response shape and exit')
    a = p.parse_args()

    day = dt.date.fromisoformat(a.date)
    if not a.curl.exists():
        sys.exit('No captured request at {}.\n'
                 'In Chrome on the campaign page: F12 > Network > reload > click the report XHR\n'
                 '> right-click > Copy > Copy as cURL (bash), and paste it into that file.'
                 .format(a.curl))

    method, url, headers, body = parse_curl(a.curl.read_text(encoding='utf-8'))
    url, u_changed = retarget(url, day)
    body, b_changed = retarget(body, day)
    changed = u_changed + b_changed
    print('{} {}'.format(method, url))
    print('  dates retargeted to {}: {}'.format(day, ', '.join(changed) or 'NONE FOUND'))
    if not changed:
        print('  ! The capture held no recognisable date, so this would refetch whatever range\n'
              '    was on screen when you copied it. Set an explicit single-day range in the\n'
              '    portal, re-capture, and try again.', file=sys.stderr)
        if not a.dry_run:
            sys.exit(2)
    if a.dry_run:
        print('  body:', (body or '')[:2000])
        return

    r = requests.request(method, url, headers=headers, data=body, timeout=60)
    if r.status_code in (401, 403) or 'login' in r.url.lower():
        sys.exit('Portal returned {} - the session cookie has expired. Re-capture the cURL.'
                 .format(r.status_code))
    r.raise_for_status()
    try:
        payload = r.json()
    except ValueError:
        sys.exit('Response was not JSON ({}). First 300 bytes:\n{}'
                 .format(r.headers.get('content-type'), r.text[:300]))

    rows = [flatten(x) for x in deepest_rows(payload)]
    if not rows:
        sys.exit('No table of rows found in the response. Re-run with --inspect to see its shape.')

    if a.inspect:
        print('\n{} rows. Keys on the first:'.format(len(rows)))
        for k, v in rows[0].items():
            print('  {:40s} {!r}'.format(k, v))
        print('\nAuto-detected mapping:', json.dumps(resolve_fields(rows[0], {}), indent=2))
        return

    override = json.loads(FIELDS.read_text()) if FIELDS.exists() else {}
    f = resolve_fields(rows[0], override)
    missing = [m for m in CANDIDATES if m not in f]
    if missing:
        sys.exit('Could not find {} among the response keys. Run --inspect, then name them\n'
                 'in {} as {{"clicks": "theRealKey", ...}}.'.format(missing, FIELDS))
    print('  fields:', ', '.join(k + '=' + str(v) for k, v in f.items()))

    gmap = json.loads(GROUPMAP.read_text()) if GROUPMAP.exists() else {}
    gmap = {k: v for k, v in gmap.items() if not k.startswith('_')}
    if not gmap:
        sys.exit('{} is empty - it maps the portal ad-group names onto AG1..AG5.\n'
                 'Run --inspect to see the names the portal uses.'.format(GROUPMAP))

    # Several portal ad groups can roll into one AG; sum them.
    metrics = ['spend', 'impressions', 'clicks', 'orders', 'revenue']
    agg, unknown = {}, set()
    for row in rows:
        name = str(row.get(f['group'], '')).strip()
        ag = gmap.get(name)
        if not ag:
            unknown.add(name)
            continue
        t = agg.setdefault(ag, dict.fromkeys(metrics, 0.0))
        for m in metrics:
            t[m] += number(row.get(f[m]))
    if unknown:
        print('  ! not in adgroup_map.json, skipped:', ', '.join(sorted(unknown)), file=sys.stderr)
    if not agg:
        sys.exit('No portal ad group matched adgroup_map.json - nothing written.')

    with (ROOT / 'data' / 'ad_group_summary.csv').open(encoding='utf-8') as fh:
        names = {r['AG']: r['Group'] for r in csv.DictReader(fh)}

    fresh = {}
    for ag, t in agg.items():
        fresh[(day.isoformat(), ag)] = [day.isoformat(), ag, names.get(ag, ''),
                                        round(t['spend'], 2), int(t['impressions']),
                                        int(t['clicks']), round(t['orders'], 2),
                                        round(t['revenue'], 2)]

    # Upsert: a refetched day replaces itself rather than doubling.
    kept = []
    if a.out.exists():
        with a.out.open(newline='', encoding='utf-8') as fh:
            for row in csv.reader(fh):
                if row and row[0] != 'Date' and (row[0], row[1]) not in fresh:
                    kept.append(row)
    kept.extend(fresh[k] for k in sorted(fresh))
    kept.sort(key=lambda r: (r[0], r[1]))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(HEAD)
        w.writerows(kept)
    print('  wrote {} rows for {} to {} ({} rows total)'.format(len(fresh), day, a.out, len(kept)))
    for k in sorted(fresh):
        print('   ', fresh[k])


if __name__ == '__main__':
    main()
