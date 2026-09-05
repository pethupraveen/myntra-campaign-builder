import pandas as pd, numpy as np, json
df = pd.read_csv('grouped.csv')

ASP, RR = 899.0, 0.30

SPEC = {
 'AG1': dict(name='Hero Scale',            active=45, pct=0.32, roas=14.0, cvr=0.045,
             thesis='Proven winners: HEALTHY status + top-decile organic demand. Ads amplify what already sells.'),
 'AG2': dict(name='Rising Stars',          active=42, pct=0.30, roas=10.5, cvr=0.036,
             thesis='High organic demand, near-zero ad exposure. The biggest untapped pool in the catalogue.'),
 'AG3': dict(name='New Launch Incubator',  active=25, pct=0.13, roas=6.0,  cvr=0.026,
             thesis='Live under 120 days with early traction. Buys ranking signal in the launch window.'),
 'AG4': dict(name='Steady Volume',         active=30, pct=0.20, roas=8.0,  cvr=0.029,
             thesis='Mid-tier consistent performers. Efficiency base that holds blended ROI up.'),
 'AG5': dict(name='Ad-Dependent Retest',   active=10, pct=0.05, roas=5.5,  cvr=0.022,
             thesis='Previously advertised, weak organic. Small controlled retest at the ROI floor.'),
 'AG6': dict(name='Dormant - Excluded',    active=0,  pct=0.00, roas=0.0,  cvr=0.0,
             thesis='No ad spend. Fix listing quality, price or imagery before paying for traffic.'),
}
MONTHLY = 15000.0
MIN_AG_MONTHLY   = 2500.0    # Myntra will not accept an ad group funded below this
MIN_CAMPAIGN_DAY = 250.0     # nor a campaign whose daily budget is under this
DAYS = 30

assert MONTHLY/DAYS >= MIN_CAMPAIGN_DAY, (
    f'Monthly budget {MONTHLY:,.0f} gives Rs {MONTHLY/DAYS:,.0f}/day, under the '
    f'Rs {MIN_CAMPAIGN_DAY:,.0f}/day campaign minimum (need Rs {MIN_CAMPAIGN_DAY*DAYS:,.0f}/month)')

def allocate(budget, shares):
    """Split budget by planned share, with no funded group under the portal's monthly floor.

    The shares are advisory, the floor is not. Lifting a starved group to the floor has to
    come out of the others, so this water-fills: freeze whoever lands under the floor, redivide
    what is left among the rest, repeat. If the floors themselves outrun the budget, drop the
    least-committed group outright - a group under the floor cannot be set up at all, and
    thinning everyone to keep it just fails the same check across more groups.
    """
    live = dict(shares)
    while live and MIN_AG_MONTHLY*len(live) > budget:
        live.pop(min(live, key=lambda g: (live[g], SPEC[g]['roas'])))
    out = {g: 0.0 for g in shares}; frozen = {}
    while True:
        rest = {g: sh for g, sh in live.items() if g not in frozen}
        if not rest:
            out.update(frozen); return out
        pool = budget - sum(frozen.values()); tot = sum(rest.values())
        trial = {g: pool*sh/tot for g, sh in rest.items()}
        under = [g for g, b in trial.items() if b < MIN_AG_MONTHLY]
        if not under:
            out.update(frozen); out.update(trial); return out
        for g in under: frozen[g] = MIN_AG_MONTHLY

BUD = allocate(MONTHLY, {g: s['pct'] for g, s in SPEC.items() if s['pct'] > 0})

df['Group Name'] = df['AG'].map(lambda g: SPEC[g]['name'])
df = df.sort_values(['AG','Opportunity Score'], ascending=[True,False])
df['Rank in Group'] = df.groupby('AG').cumcount()+1
# a group the floor priced out of the plan gets no spend, so its styles queue instead
df['Status'] = np.where(df['AG']=='AG6','EXCLUDED',
                np.where((df['Rank in Group']<=df['AG'].map(lambda g:SPEC[g]['active']))
                         & (df['AG'].map(lambda g: BUD.get(g,0.0))>0), 'ACTIVE','QUEUE'))

rows=[]
for g,s in SPEC.items():
    sub=df[df.AG==g]; act=(sub.Status=='ACTIVE').sum()
    bud = BUD.get(g,0.0)
    cpc = (ASP*s['cvr']*(1-RR)/s['roas']) if s['roas'] else 0
    clicks = bud/cpc if cpc else 0
    orders = clicks*s['cvr']
    rev = orders*ASP*(1-RR)
    rows.append(dict(AG=g, Group=s['name'], Total=len(sub), Active=act, Queue=(sub.Status=='QUEUE').sum(),
        Pct=bud/MONTHLY, Monthly=bud, Daily=bud/DAYS, TargetROAS=s['roas'], CVR=s['cvr'],
        MaxCPC=round(cpc,2), Clicks=round(clicks), Orders=round(orders,1), NetRevenue=round(rev),
        PerStyleMonth=round(bud/act,1) if act else 0, Thesis=s['thesis']))
summary=pd.DataFrame(rows)

df['Max CPC']   = df['AG'].map(lambda g: round(ASP*SPEC[g]['cvr']*(1-RR)/SPEC[g]['roas'],2) if SPEC[g]['roas'] else 0)
df['Target ROI']= df['AG'].map(lambda g: SPEC[g]['roas'])
mb = summary.set_index('AG')['Monthly'].to_dict()
# weight per-style budget by opportunity score within active set
df['Monthly Budget'] = 0.0
for g in SPEC:
    m=(df.AG==g)&(df.Status=='ACTIVE')
    if m.sum():
        w=df.loc[m,'Opportunity Score']; alloc=(mb[g]*w/w.sum()).round(0)
        alloc.iloc[0]+= mb[g]-alloc.sum()          # absorb rounding drift in the top-ranked style
        df.loc[m,'Monthly Budget']=alloc
df['Daily Budget']=(df['Monthly Budget']/DAYS).round(1)

blended = (summary.Monthly*summary.TargetROAS).sum()/MONTHLY
print(summary.drop(columns='Thesis').to_string(index=False))
print(f"\nBLENDED ROAS: {blended:.2f}x  (corridor 5.5-15.5)")
print(f"TOTAL BUDGET: Rs {summary.Monthly.sum():,.0f} | ACTIVE STYLES: {summary.Active.sum()} | QUEUE: {summary.Queue.sum()}")
print(f"PROJECTED: {summary.Clicks.sum():,.0f} clicks | {summary.Orders.sum():.0f} orders | Rs {summary.NetRevenue.sum():,.0f} net revenue")
print(f"Budget check: {df['Monthly Budget'].sum():,.0f} | rows {len(df)}")
funded = summary[summary.Monthly>0]
print(f"FLOORS: campaign Rs {MONTHLY/DAYS:,.0f}/day vs Rs {MIN_CAMPAIGN_DAY:,.0f} min | "
      f"smallest ad group Rs {funded.Monthly.min():,.0f}/mo vs Rs {MIN_AG_MONTHLY:,.0f} min | "
      f"{len(funded)} groups funded")
df.to_csv('final.csv',index=False); summary.to_csv('summary.csv',index=False)
json.dump({'asp':ASP,'rr':RR,'monthly':MONTHLY,'blended':round(blended,2)},open('params.json','w'))
