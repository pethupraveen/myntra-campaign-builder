import pandas as pd, numpy as np, json
df = pd.read_csv('scored.csv')

def assign(r):
    ds, sat, days, adv, health = r['Demand Score'], r['Ad Saturation'], r['Days Live'], r['Ever Advertised'], r['Health']
    if health=='HEALTHY' and ds>=78: return 'AG1'
    if ds>=78:                       return 'AG2'
    if days<=120 and ds>=50:         return 'AG3'
    if ds>=45:                       return 'AG4'
    if adv:                          return 'AG5'
    return 'AG6'

df['AG'] = df.apply(assign, axis=1)
print(df['AG'].value_counts().sort_index())
print()
print(df.groupby('AG').agg(styles=('Style Id','size'),
    med_demand=('Demand Score','median'), med_vel=('Organic/Day','median'),
    tot_organic=('Organic Impressions','sum'), med_days=('Days Live','median'),
    ever_ad=('Ever Advertised','sum')).round(2).to_string())
df.to_csv('grouped.csv',index=False)
