import pandas as pd, numpy as np, json
from datetime import datetime

TODAY = pd.Timestamp('2026-09-02')
df = pd.read_csv('data.csv')
df['Live Since'] = pd.to_datetime(df['Live Since'], format='%d-%m-%Y')
df['Days Live'] = (TODAY - df['Live Since']).dt.days.clip(lower=1)

df['Organic/Day'] = df['Organic Impressions'] / df['Days Live']
df['Ad Saturation'] = np.where(df['Total Impressions']>0, df['Inorganic Impressions']/df['Total Impressions'], 0)
df['Ever Advertised'] = df['Inorganic Impressions'] > 0

# percentile ranks (0-100)
df['P_Reach'] = df['Organic Impressions'].rank(pct=True)*100
df['P_Velocity'] = df['Organic/Day'].rank(pct=True)*100
# freshness: styles live 30-180 days get the bonus (proven enough, still current)
age = df['Days Live']
fresh = np.select(
    [age<=30, (age>30)&(age<=180), (age>180)&(age<=365), age>365],
    [70, 100, 60, 30]
)
df['Freshness'] = fresh

df['Demand Score'] = (0.50*df['P_Reach'] + 0.35*df['P_Velocity'] + 0.15*df['Freshness']).round(1)
# untapped upside: high demand, low prior ad exposure
df['Opportunity Score'] = (df['Demand Score'] * (1 - 0.6*df['Ad Saturation'])).round(1)

df.to_csv('scored.csv', index=False)

print(df[['Days Live','Organic/Day','Demand Score','Opportunity Score']].describe().round(2).to_string())
print()
print('Demand Score deciles:')
for q in [.5,.7,.8,.85,.9,.95,.98]:
    print(f'  p{int(q*100)}: {df["Demand Score"].quantile(q):.1f}  (velocity p{int(q*100)}: {df["Organic/Day"].quantile(q):.2f}/day)')
print()
print('HEALTHY styles demand score:', df[df.Health=="HEALTHY"]["Demand Score"].describe().round(1).to_dict())
print('Age buckets:'); print(pd.cut(df['Days Live'],[0,30,60,120,180,365,10000]).value_counts().sort_index())
