# Myntra Campaign Builder

Style-level Myntra PLA (Product Listing Ads) campaign planner for a 4,382-SKU catalogue on a
₹15,000/month budget, targeting a 5.5x–15.5x ROI corridor.

Scores every live style on organic demand, ad saturation and age, sorts them into six ad groups,
derives a max CPC bid per group from an explicit ROI target, and ships a performance dashboard
plus a formula-driven Excel workbook for weekly optimisation.

## The finding that drives the plan

**4,144 of 4,382 styles have never received a single paid impression**, yet they carry 3.5M organic
impressions between them. The catalogue is not short of demand — it is short of budget.

₹15,000/month is ₹500/day. Spread across 4,382 styles that is 11 paise per style per day, which
wins no auctions. So the plan funds **152 styles** and deliberately excludes 1,955.

## Ad groups

| AG  | Name                 | Selection rule                          | Pool  | Live | Budget      | Target ROI | Max CPC¹ |
|-----|----------------------|-----------------------------------------|-------|------|-------------|------------|----------|
| AG1 | Hero Scale           | `HEALTHY` and Demand Score ≥ 78          | 121   | 45   | ₹3,871 (26%) | 14.0x      | ₹2.02    |
| AG2 | Rising Stars         | Demand Score ≥ 78                        | 591   | 42   | ₹3,629 (24%) | 10.5x      | ₹2.16    |
| AG3 | New Launch Incubator | ≤ 120 days live and Demand Score 50–78   | 127   | 25   | ₹2,500 (17%) | 6.0x       | ₹2.73    |
| AG4 | Steady Volume        | Demand Score 45–78                       | 1,535 | 30   | ₹2,500 (17%) | 8.0x       | ₹2.28    |
| AG5 | Ad-Dependent Retest  | Demand Score < 45 with past paid impr.   | 53    | 10   | ₹2,500 (17%) | 5.5x       | ₹2.52    |
| AG6 | Dormant — Excluded   | Demand Score < 45, never advertised      | 1,955 | 0    | ₹0           | —          | —        |

¹ at the default ₹899 ASP / 30% return-rate assumption.

Budget-weighted blend: **9.40x** — mid-corridor, with room to absorb a bad week.
Projection: 6,602 clicks, 224 orders, ₹1,41,049 net revenue per month, ₹67 per order.

### The portal minimums set the shares

Myntra will not accept an ad group funded under **₹2,500 a month**, or a campaign whose daily budget
is under **₹250**. These are not preferences — a plan that ignores them cannot be entered at all.

That floor, not the strategy, is what fixes three of the five shares. The intended split was 32/30/13/20/5;
on ₹15,000 that puts AG3 at ₹1,950 and AG5 at ₹750, both rejected at setup. `src/model.py` water-fills
instead: anyone landing under the floor is pinned to it, and what remains is redivided among the rest
until every funded group clears. AG3, AG4 and AG5 all end up pinned at ₹2,500, leaving ₹7,500 to split
between AG1 and AG2 in their original 32:30 ratio.

The cost is visible: forcing ₹2,500 into the weakest group pulls the blend from 10.29x to 9.40x, and
gives AG5 ₹250 per style per month against AG1's ₹86. Five groups is the most ₹15,000 supports
(5 × ₹2,500 = ₹12,500). If the floors ever outrun the budget, the model drops the least-committed
group rather than thinning everyone below the line.

### Why a ladder rather than one target

A flat 15.5x target would starve discovery — new styles have no conversion history and would never
clear the bar. A flat 5.5x would leave money on the proven winners. Each group sits on its own rung
and the blend lands inside the corridor.

## Scoring

```
Days Live        = today − Live Since
Organic/Day      = Organic Impressions ÷ Days Live
Ad Saturation    = Inorganic Impressions ÷ Total Impressions

Demand Score     = 0.50 · pct_rank(Organic Impressions)
                 + 0.35 · pct_rank(Organic/Day)
                 + 0.15 · freshness            (≤30d: 70, 31–180d: 100, 181–365d: 60, >365d: 30)

Opportunity Score = Demand Score × (1 − 0.6 × Ad Saturation)
```

`Organic/Day` removes the age advantage an older style gets from simple accumulation.
`Opportunity Score` discounts styles whose visibility was bought rather than earned, which surfaces
proven organic demand that has never been paid for — the cheapest wins available.

Within each group, styles are ranked by Opportunity Score. The top N go live; the rest form a ranked
rotation queue.

## Bid model

```
Max CPC = ASP × CVR × (1 − return rate) ÷ target ROI
```

Bid at or under this and a group cannot fall below its ROI target while conversion holds. Note that
ROI does not move when ASP or return rate change — the bid absorbs it. Price and returns set what a
click is worth, not what return you accept.

Group CVR assumptions: AG1 4.5%, AG2 3.6%, AG3 2.6%, AG4 2.9%, AG5 2.2%.

## Layout

```
src/                 scoring and planning pipeline (run in order)
  engine.py            derives Days Live, Organic/Day, Ad Saturation, Demand + Opportunity Score
  groups.py            assigns each style to an ad group
  model.py             sizes budgets, derives bids, allocates per-style spend
  build_xlsx.py        builds the Excel workbook
  fetch_daily.py       replays the captured portal request for one day -> data/daily_log.csv
  Write-DailyTracker.ps1  pushes that CSV into the workbook's Daily Tracker over Excel COM
  Get-DailyLog.ps1     both of the above, one call
config/              adgroup_map.json — portal ad-group name -> AG1..AG5
                     myntra_fields.json — optional overrides when a metric is not auto-detected
secrets/             the captured browser request (gitignored, holds your session cookie)
data/                styles_scored.csv — all 4,382 styles with scores, group and status
                     ad_group_summary.csv — the six groups with budgets, bids and projections
                     model_names.csv — Style Id -> phone model, labelling every one of the 4,382
index.html           the plan — how the budget splits, the roster, the bid calculator, the
                     playbook (no build step, no dependencies, no server)
daily/index.html     the Daily Desk — log each day, read the performance back, keep the record
output/              Myntra_Campaign_Builder.xlsx — 9 tabs, formula-driven from a Control Panel
docs/                strategy one-pager and weekly optimisation SOP
```

## Running it

```bash
pip install pandas numpy openpyxl
python src/engine.py       # data.csv -> scored.csv
python src/groups.py       # scored.csv -> grouped.csv
python src/model.py        # grouped.csv -> final.csv, summary.csv
python src/build_xlsx.py   # + data/model_names.csv -> Myntra_Campaign_Builder.xlsx
```

The roster, queue and excluded lists are one filter off the master rather than their own
files — `csvgrep -c Status -m ACTIVE data/styles_scored.csv`, or `Status == "QUEUE"` /
`"EXCLUDED"` — and the workbook ships all three as separate tabs.

Input is a CSV named `data.csv` with columns:
`Style Id, Live Since (DD-MM-YYYY), Organic Impressions, Inorganic Impressions, Total Impressions, Health, Reasons`.

Open `index.html` directly in a browser — it needs no server.

### Live dashboard

`.github/workflows/pages.yml` deploys the site to GitHub Pages on every push to `main` — the plan
at the root, the Daily Desk at `/daily/`.
Enable it once at **Settings → Pages → Source: GitHub Actions**, and the site goes live at
`https://<your-username>.github.io/myntra-campaign-builder/`.

## Tracking the campaign day to day

Two tabs, one in and one out.

**`Daily Tracker`** — the input. Five rows a day, at **ad-group level**. Per style the daily numbers
are noise (1.2–3.3 clicks, 0.03–0.07 orders a day); per group they are signal (31–64 clicks, 0.7–2.9 orders).
Type spend, impressions, clicks, orders and gross revenue into the yellow columns; pace, CTR, actual
vs max CPC, cumulative CVR and cumulative ROI compute themselves, and a one-word `Flag` marks the
row.

**`Daily Action Plan`** — the output. Put a date in `B4` and it reads that day back as a ranked plan:
a `DO FIRST` line, a per-group reading, and a named action for each of the five groups.

Every group lands on a priority code, and the code decides what it says:

| | | |
|---|---|---|
| 1 | NO DELIVERY | zero impressions — bid under the auction floor, or out of stock |
| 2 | UNDERSPENDING | pace below 60% — bids are not clearing auctions |
| 3 | OVERSPEND | pace above 115% — the daily cap is set wrong |
| 4 | BID-CAPPED | actual CPC pinned at max — bid-constrained, not budget-constrained |
| 5 | BELOW FLOOR | cumulative ROI under the floor — cut the bid 20% |
| 6 | ABOVE CEILING | cumulative ROI over the ceiling — raise the bid 15%, move budget in |
| 7 | HOLD | still collecting, or inside the corridor — change nothing |

The split matters. **1–4 are mechanical facts**, true the same day you read them: they say nothing
about whether the campaign works, only whether the money is reaching the auction, and you fix them
immediately. **5–6 are statistics**, and stay hidden until the group has 40 cumulative clicks and 10
cumulative orders — so no bid moves on a three-day sample. A delivery fault always outranks a bid
decision, because a group spending 40% of target has no ROI worth reading.

`docs/strategy-and-sop.md` has the daily loop and the delivery-fault table.

### The Daily Desk

`daily/index.html` is the tracker as a web form, at
`https://<your-username>.github.io/myntra-campaign-builder/daily/`. Pick a date, type the five rows,
and pace, CPC, CTR, CVR, ROI and the flag compute as you type — the same formulas as the `Daily
Tracker` columns I onwards. Three tabs: **Log the day**, **Performance** (blended ROI against the
corridor, spend against target, per-group table, today's ranked actions) and **Records** (every saved
day, editable, deletable, exportable as a CSV with one row per group per day).

Where it saves depends on where it runs. Published as a Claude Artifact it writes each day to the
artifact database as `days/YYYY-MM-DD`, so the record follows the account and several people see the
same history. Served from GitHub Pages there is no database, so it keeps the days in that browser's
local storage instead and says so on screen — export the CSV to move them. The **Assumptions** panel
is the Control Panel's blue cells: budget, return rate, ROI floor and ceiling, days in month. Group
shares stay pinned to the ₹15,000 baseline, so changing the budget rescales every daily target and
every Max CPC the way `Control Panel` does.

Already have days in the workbook? **Records → Import from the workbook** takes a paste: select the
filled `Daily Tracker` rows from column A across to `Gross Rev` (column H), copy, paste. Columns are
read by position from the `AG` cell, so extra columns and header rows are ignored, a blank cell in a
logged day counts as zero, and an entirely blank day is skipped. Dates copied as `07-Sep` carry no
year in the clipboard: the importer assumes the current year and rolls forward when the sequence
steps backwards, so format the column as `dd-mmm-yyyy` before copying if a log crosses a year
boundary. Days that already exist are named before anything is replaced.

Nothing is logged yet on a fresh page, so it opens on six clearly-marked sample days — the first save
clears them.

### Pulling the day from the portal

The numbers are typed into the Desk or the workbook by hand, or fetched from the ads portal by
`src/fetch_daily.py`.

Myntra publishes no ad API and issues no service credential — the report you read at
`advertising.myntra.com/ad-user/product-listing-ads/CMP2496557` is an XHR the page makes for
itself, authenticated by your seller session cookie. So the request is not written into this
repo: it is **captured once from your browser and replayed with the date swapped**.

**Capture it.** In Chrome, on the campaign page, set the date range to a single day. Then
`F12` → **Network** → reload → click the request that returns the ad-group table → right-click →
**Copy → Copy as cURL (bash)** → paste the whole thing into `secrets/myntra_curl.txt`.
That file holds a live session cookie and is gitignored. Re-capture when it expires — usually
days to weeks; the fetcher says so plainly when it does.

**Run it.**

```powershell
powershell -File src/Get-DailyLog.ps1                     # yesterday, CSV + workbook
powershell -File src/Get-DailyLog.ps1 -Date 2026-09-09
powershell -File src/Get-DailyLog.ps1 -CsvOnly            # leave the workbook alone
```

Or the two halves on their own:

```bash
python src/fetch_daily.py --date 2026-09-09 --dry-run   # show the request, send nothing
python src/fetch_daily.py --date 2026-09-09 --inspect   # dump the response keys and rows
python src/fetch_daily.py --date 2026-09-09
```

Every date in the captured URL and body is rewritten to the day you ask for — ISO, `dd-mm-yyyy`
and epoch-millisecond stamps, the last keeping its time of day so a range start stays a start
and an end stays an end. If the capture carried no date at all the fetcher refuses to send,
rather than silently refetching whatever range was on screen when you copied it.

The response is read structurally, not by a hardcoded schema: the longest list of objects in it
is the report table, and the metric columns are matched by name (`adGroupName`, `metrics.spend`,
`impressions`, `clicks`, `orders`, `revenue` and the usual variants). When a metric cannot be
found, `--inspect` prints every key it saw and you name the right one in
`config/myntra_fields.json`. Portal ad groups are rolled up to `AG1`–`AG5` through
`config/adgroup_map.json`; several portal groups may map to one AG and their numbers are summed,
and anything unmapped is named and skipped rather than quietly dropped.

Results land in `data/daily_log.csv` — `Date,AG,Group,Spend,Impressions,Clicks,Orders,GrossRev`,
one row per group per day, upserted, so refetching a day corrects it instead of doubling it.
That header is the Daily Desk's export header truncated to the input columns, so the file also
pastes into **Records → Import from the workbook**.

`Write-DailyTracker.ps1` then writes only the five yellow input columns (D–H) of the `Daily
Tracker` tab, in place over Excel COM — the workbook carries days you typed that nothing in
`src/` can regenerate, so it is edited, never rebuilt. It locates each row by arithmetic off the
start date in `B5` and then checks the `AG` code actually sitting in column B before writing, so
a moved layout stops the run instead of filling in the wrong group. A day outside the 31-day
window is reported and skipped. If you already have the workbook open, your own Excel instance
is reused rather than killed. `-WhatIf` shows every row it would touch and writes nothing.

## Assumptions to replace with real numbers

The bid math is only as good as its inputs. Three are currently assumptions, flagged everywhere they
are used and exposed as sliders in the dashboard and yellow input cells in the workbook:

- **ASP ₹899** — a blended placeholder. Per-style selling price turns one bid per group into a bid per style.
- **Return rate 30%** — typical for Myntra apparel. Returns are the quietest ROI killer: a reported 8x is a real 5.6x at 30% returns.
- **Group CVR** — modelled from demand percentile, not measured. Historical conversion data replaces these directly.

Category per style would also help materially; auction floors differ a lot between, say, kurtas and footwear.

## Data vintage

Impressions data as of 21 Aug 2026; scored 02 Sep 2026. Re-score roughly every 8 weeks — about 15%
of the roster turns over each cycle as styles age and new ones go live.
