import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

df=pd.read_csv('final.csv'); summ=pd.read_csv('summary.csv')
wb=Workbook(); ARIAL='Arial'
BLUE=Font(name=ARIAL,size=10,color='0000FF'); BLK=Font(name=ARIAL,size=10)
HDR=Font(name=ARIAL,size=10,bold=True,color='FFFFFF')
HFILL=PatternFill('solid',fgColor='1F3864'); YFILL=PatternFill('solid',fgColor='FFFF00')
TITLE=Font(name=ARIAL,size=14,bold=True,color='1F3864')
SUB=Font(name=ARIAL,size=10,italic=True,color='595959')
BOLD=Font(name=ARIAL,size=10,bold=True)
thin=Side(style='thin',color='BFBFBF'); BOX=Border(thin,thin,thin,thin)

def hdr(ws,row,cols,widths):
    for i,(c,w) in enumerate(zip(cols,widths),1):
        cell=ws.cell(row=row,column=i,value=c); cell.font=HDR; cell.fill=HFILL
        cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes=ws.cell(row=row+1,column=1)

# ---------------- 1. Control Panel ----------------
ws=wb.active; ws.title='Control Panel'
ws['A1']='MYNTRA CAMPAIGN BUILDER — CONTROL PANEL'; ws['A1'].font=TITLE
ws['A2']='Every number in this workbook recalculates from the blue cells below. Change a blue cell and the whole plan updates.'; ws['A2'].font=SUB
ws['A4']='GLOBAL ASSUMPTIONS'; ws['A4'].font=BOLD
inputs=[('Monthly Ad Budget (Rs)',15000,'"#,##0','User-provided'),
        ('Average Selling Price / ASP (Rs)',899,'#,##0','ASSUMPTION - user said ASP varies; replace with your blended ASP'),
        ('Return / RTO Rate',0.30,'0.0%','ASSUMPTION - typical Myntra apparel range 25-35%'),
        ('ROI Floor (min acceptable ROAS)',5.5,'0.0"x"','User-provided goal'),
        ('ROI Ceiling (stretch ROAS)',15.5,'0.0"x"','User-provided goal'),
        ('Days in Month',30,'0','Standard')]
r=5
for lbl,val,fmt,note in inputs:
    ws.cell(row=r,column=1,value=lbl).font=BLK
    c=ws.cell(row=r,column=2,value=val); c.font=BLUE; c.fill=YFILL; c.number_format=fmt.replace('"#,##0','#,##0'); c.border=BOX
    ws.cell(row=r,column=3,value=note).font=SUB
    r+=1
ws.column_dimensions['A'].width=36; ws.column_dimensions['B'].width=14; ws.column_dimensions['C'].width=72

ws['A12']='AD GROUP LEVERS  — edit Budget %, Target ROI and CVR per group'; ws['A12'].font=BOLD
gcols=['Ad Group','Group Name','Active Styles','Budget %','Target ROI (ROAS)','Assumed CVR','Monthly Budget (Rs)','Daily Budget (Rs)','Max CPC Bid (Rs)','Est. Clicks/mo','Est. Orders/mo','Est. Net Revenue (Rs)']
hdr(ws,13,gcols,[11,24,13,10,15,12,17,16,15,14,14,19])
ws.freeze_panes=None
r=14
for _,s in summ.iterrows():
    ws.cell(row=r,column=1,value=s.AG).font=BLK
    ws.cell(row=r,column=2,value=s.Group).font=BLK
    ws.cell(row=r,column=3,value=int(s.Active)).font=BLK
    for col,val,fmt in [(4,s.Pct,'0%'),(5,s.TargetROAS,'0.0"x"'),(6,s.CVR,'0.00%')]:
        c=ws.cell(row=r,column=col,value=val); c.font=BLUE; c.fill=YFILL; c.number_format=fmt; c.border=BOX
    ws.cell(row=r,column=7,value=f'=$B$5*D{r}').number_format='#,##0'
    ws.cell(row=r,column=8,value=f'=G{r}/$B$10').number_format='#,##0.0'
    ws.cell(row=r,column=9,value=f'=IF(E{r}=0,0,$B$6*F{r}*(1-$B$7)/E{r})').number_format='#,##0.00'
    ws.cell(row=r,column=10,value=f'=IF(I{r}=0,0,G{r}/I{r})').number_format='#,##0'
    ws.cell(row=r,column=11,value=f'=J{r}*F{r}').number_format='#,##0.0'
    ws.cell(row=r,column=12,value=f'=K{r}*$B$6*(1-$B$7)').number_format='#,##0'
    for col in range(1,13): ws.cell(row=r,column=col).border=BOX
    r+=1
tot=r
ws.cell(row=tot,column=2,value='PORTFOLIO TOTAL').font=BOLD
for col,f,fmt in [(3,f'=SUM(C14:C{r-1})','0'),(4,f'=SUM(D14:D{r-1})','0%'),(7,f'=SUM(G14:G{r-1})','#,##0'),
                  (8,f'=SUM(H14:H{r-1})','#,##0.0'),(10,f'=SUM(J14:J{r-1})','#,##0'),
                  (11,f'=SUM(K14:K{r-1})','#,##0.0'),(12,f'=SUM(L14:L{r-1})','#,##0')]:
    c=ws.cell(row=tot,column=col,value=f); c.font=BOLD; c.number_format=fmt; c.border=BOX
c=ws.cell(row=tot,column=5,value=f'=IF(G{tot}=0,0,L{tot}/G{tot})'); c.font=BOLD; c.number_format='0.00"x"'; c.border=BOX

ws.cell(row=tot+2,column=1,value='BLENDED PORTFOLIO ROI').font=BOLD
c=ws.cell(row=tot+2,column=2,value=f'=E{tot}'); c.font=BOLD; c.number_format='0.00"x"'
ws.cell(row=tot+2,column=3,value=f'=IF(AND(E{tot}>=$B$8,E{tot}<=$B$9),"INSIDE TARGET CORRIDOR 5.5x - 15.5x","OUT OF CORRIDOR - REBALANCE")').font=BOLD
ws.cell(row=tot+3,column=1,value='Cost per Order (Rs)').font=BLK
ws.cell(row=tot+3,column=2,value=f'=IF(K{tot}=0,0,G{tot}/K{tot})').number_format='#,##0.0'
ws.cell(row=tot+4,column=1,value='Budget check (must equal Monthly Budget)').font=BLK
ws.cell(row=tot+4,column=2,value=f'=G{tot}').number_format='#,##0'

ws.cell(row=tot+6,column=1,value='BID FORMULA').font=BOLD
ws.cell(row=tot+7,column=1,value='Max CPC  =  ASP  x  CVR  x  (1 - Return Rate)  /  Target ROAS').font=BLK
ws.cell(row=tot+8,column=1,value='Bid at or below this and the group cannot fall under its ROI target, provided CVR holds.').font=SUB
ws.cell(row=tot+10,column=1,value='LEGEND').font=BOLD
ws.cell(row=tot+11,column=1,value='Yellow fill + blue text = your input cells. Everything else is a formula - do not overwrite.').font=SUB
ws.cell(row=tot+12,column=1,value='Style-level tabs: Active Roster (spend now) | Rotation Queue (next in line) | Excluded (no ad spend).').font=SUB

# ---------------- 2. Ad Group Strategy ----------------
ws2=wb.create_sheet('Ad Group Strategy')
ws2['A1']='AD GROUP STRATEGY & SELECTION RULES'; ws2['A1'].font=TITLE
hdr(ws2,3,['Ad Group','Group Name','Selection Rule','Investment Thesis','Styles in Pool','Active Now','Rotation Queue','Target ROI'],[10,22,52,62,13,11,15,11])
rules={'AG1':'Health = HEALTHY  AND  Demand Score >= 78',
       'AG2':'Demand Score >= 78  (not already in Hero Scale)',
       'AG3':'Live <= 120 days  AND  Demand Score 50 - 78',
       'AG4':'Demand Score 45 - 78',
       'AG5':'Demand Score < 45  AND  has past paid impressions',
       'AG6':'Demand Score < 45  AND  never advertised'}
r=4
for _,s in summ.iterrows():
    vals=[s.AG,s.Group,rules[s.AG],s.Thesis,int(s.Total),int(s.Active),int(s.Queue),s.TargetROAS]
    for i,v in enumerate(vals,1):
        c=ws2.cell(row=r,column=i,value=v); c.font=BLK; c.border=BOX
        c.alignment=Alignment(wrap_text=True,vertical='top')
    ws2.cell(row=r,column=8).number_format='0.0"x"'
    ws2.row_dimensions[r].height=42
    r+=1
ws2.cell(row=r+1,column=1,value='SCORING METHOD').font=BOLD
for i,t in enumerate([
 'Days Live = 02-Sep-2026 minus Live Since date.',
 'Organic/Day = Organic Impressions / Days Live  -> demand velocity, removes the age advantage of older styles.',
 'Ad Saturation = Inorganic Impressions / Total Impressions  -> how much of the visibility was bought.',
 'Demand Score = 50% percentile-rank of Organic Impressions + 35% percentile-rank of Organic/Day + 15% freshness score.',
 'Opportunity Score = Demand Score x (1 - 0.6 x Ad Saturation)  -> rewards proven demand that has never been paid for.',
 'Active Now = top N by Opportunity Score within each group, N sized so each active style gets a meaningful daily budget.']):
    ws2.cell(row=r+2+i,column=1,value=t).font=SUB

# ---------------- style tabs ----------------
cols=['Style Id','Model Name (fill in)','Ad Group','Group Name','Rank in Group','Live Since','Days Live',
      'Organic Impressions','Inorganic Impressions','Total Impressions','Organic/Day','Ad Saturation',
      'Demand Score','Opportunity Score','Health','Max CPC Bid (Rs)','Monthly Budget (Rs)','Daily Budget (Rs)','Target ROI','Status']
widths=[12,26,10,21,13,12,10,13,13,12,11,11,11,12,10,13,14,13,10,11]
gmap={ag:14+i for i,ag in enumerate(summ.AG)}

def style_tab(name,data,title,note,budgets=True):
    w=wb.create_sheet(name)
    w['A1']=title; w['A1'].font=TITLE
    w['A2']=note; w['A2'].font=SUB
    hdr(w,4,cols,widths); w.freeze_panes='C5'
    for i,(_,x) in enumerate(data.iterrows()):
        r=5+i; gr=gmap[x['AG']]
        vals=[int(x['Style Id']),'',x['AG'],x['Group Name'],int(x['Rank in Group']),x['Live Since'],int(x['Days Live']),
              int(x['Organic Impressions']),int(x['Inorganic Impressions']),int(x['Total Impressions']),
              round(x['Organic/Day'],2),round(x['Ad Saturation'],3),x['Demand Score'],x['Opportunity Score'],x['Health']]
        for ci,v in enumerate(vals,1):
            c=w.cell(row=r,column=ci,value=v); c.font=BLK
        w.cell(row=r,column=2).fill=YFILL; w.cell(row=r,column=2).font=BLUE
        w.cell(row=r,column=11).number_format='#,##0.00'
        w.cell(row=r,column=12).number_format='0.0%'
        w.cell(row=r,column=16,value=f"='Control Panel'!$I${gr}").number_format='#,##0.00'
        if budgets:
            w.cell(row=r,column=17,value=round(x['Monthly Budget'],0)).number_format='#,##0'
            w.cell(row=r,column=18,value=f'=Q{r}/\'Control Panel\'!$B$10').number_format='#,##0.0'
        w.cell(row=r,column=19,value=f"='Control Panel'!$E${gr}").number_format='0.0"x"'
        w.cell(row=r,column=20,value=x['Status'])
        for ci in range(1,21): w.cell(row=r,column=ci).border=BOX
    return w

act=df[df.Status=='ACTIVE'].sort_values(['AG','Rank in Group'])
que=df[df.Status=='QUEUE'].sort_values(['AG','Rank in Group'])
exc=df[df.Status=='EXCLUDED'].sort_values('Demand Score',ascending=False)

style_tab('Active Roster',act,'ACTIVE ROSTER - 152 STYLES GETTING SPEND NOW',
 'Set these up in Myntra Partner Portal. Column B is yours to fill with model names — send them to me and I will label every row.')
style_tab('Rotation Queue',que,'ROTATION QUEUE - NEXT IN LINE',
 'Ranked by Opportunity Score. When an active style misses its ROI target for 2 weeks, pause it and promote the top queued style in the same group.',budgets=False)
style_tab('Excluded - Dormant',exc,'EXCLUDED - NO AD SPEND',
 'Demand Score below 45 with no ad history. Paying for traffic here burns budget. Fix images, title keywords, price or size availability first, then re-score.',budgets=False)

# ---------------- Weekly Tracker ----------------
wt=wb.create_sheet('Weekly Tracker')
wt['A1']='WEEKLY PERFORMANCE TRACKER'; wt['A1'].font=TITLE
wt['A2']='Fill the blue columns each Monday from your Myntra ads report. ROI, CPC and the action call compute themselves.'; wt['A2'].font=SUB
tc=['Week Starting','Ad Group','Spend (Rs)','Impressions','Clicks','Orders','Gross Revenue (Rs)','Returns (Rs)','Net Revenue (Rs)','CTR','CVR','Actual CPC (Rs)','Actual ROI','vs Target','ACTION']
hdr(wt,4,tc,[14,20,12,13,10,10,16,13,15,9,9,13,11,11,34])
ex=['2026-09-07','AG1 Hero Scale',1120,48000,555,26,23400,7020,None,None,None,None,None,None,None]
for i,v in enumerate(ex,1):
    if v is not None:
        c=wt.cell(row=5,column=i,value=v); c.font=BLUE; c.fill=YFILL
wt.cell(row=5,column=15)
for r in range(5,45):
    for col in [1,2,3,4,5,6,7,8]:
        c=wt.cell(row=r,column=col)
        if r>5: c.fill=YFILL; c.font=BLUE
        c.border=BOX
    wt.cell(row=r,column=9,value=f'=IF(C{r}="","",G{r}-H{r})').number_format='#,##0'
    wt.cell(row=r,column=10,value=f'=IF(OR(D{r}="",D{r}=0),"",E{r}/D{r})').number_format='0.00%'
    wt.cell(row=r,column=11,value=f'=IF(OR(E{r}="",E{r}=0),"",F{r}/E{r})').number_format='0.00%'
    wt.cell(row=r,column=12,value=f'=IF(OR(E{r}="",E{r}=0),"",C{r}/E{r})').number_format='#,##0.00'
    wt.cell(row=r,column=13,value=f'=IF(OR(C{r}="",C{r}=0),"",I{r}/C{r})').number_format='0.00"x"'
    wt.cell(row=r,column=14,value=f'=IFERROR(IF(M{r}="","",M{r}-IFERROR(INDEX(\'Control Panel\'!$E$14:$E$19,MATCH(LEFT(B{r},3),\'Control Panel\'!$A$14:$A$19,0)),0)),"")').number_format='+0.0"x";-0.0"x"'
    wt.cell(row=r,column=15,value=f'=IF(M{r}="","",IF(M{r}<\'Control Panel\'!$B$8,"BELOW FLOOR - cut bid 20% or pause",IF(M{r}>\'Control Panel\'!$B$9,"ABOVE CEILING - raise bid 15%, scale budget",IF(N{r}<0,"Under target - trim bid 10%","On track - hold or scale"))))').font=BOLD
    for col in range(9,16): wt.cell(row=r,column=col).border=BOX
wt.freeze_panes='A5'

# ---------------- Master ----------------
mdf=df[['Style Id','AG','Group Name','Status','Live Since','Days Live','Organic Impressions','Inorganic Impressions',
        'Total Impressions','Organic/Day','Ad Saturation','Demand Score','Opportunity Score','Health','Rank in Group']].copy()
mdf.insert(1,'Model Name (fill in)','')
mw=wb.create_sheet('Master Data')
mw['A1']='MASTER - ALL 4,382 STYLES SCORED'; mw['A1'].font=TITLE
hdr(mw,3,list(mdf.columns),[12,26,9,21,11,12,10,13,13,12,11,11,11,12,10,13])
for i,row in enumerate(mdf.itertuples(index=False)):
    for ci,v in enumerate(row,1):
        c=mw.cell(row=4+i,column=ci,value=(round(v,3) if isinstance(v,float) else v)); c.font=BLK
mw.freeze_panes='C4'
wb.save('Myntra_Campaign_Builder.xlsx')
print('saved')
