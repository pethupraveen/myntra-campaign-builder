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

# ---------------- Daily Tracker ----------------
# Tracked per AD GROUP, not per style. At Rs 3.3/style/day a style yields ~1.7 clicks and
# ~0.05 orders a day - unreadable. A group yields 10-79 clicks and 0.2-3.6 orders a day.
DAYS=31; GRP=['AG1','AG2','AG3','AG4','AG5']
LH=21; LS=22; LE=LS+DAYS*len(GRP)-1                      # log header / first row / last row
dt=wb.create_sheet('Daily Tracker')
dt['A1']='DAILY CAMPAIGN TRACKER — BY AD GROUP'; dt['A1'].font=TITLE
dt['A2']='Enter the yellow columns once a day — 5 rows, about two minutes. Everything right of column H computes itself.'; dt['A2'].font=SUB
dt['A3']='Track by ad group, never by style. One style gets ~1.7 clicks and 0.05 orders a day: a single order swings its ROI by 300%. A group gets 10-79 clicks a day, which is decision-grade.'; dt['A3'].font=SUB

ws_cp="'Control Panel'"
def cp(col,row):   return f"INDEX({ws_cp}!${col}$14:${col}$19,MATCH($B{row},{ws_cp}!$A$14:$A$19,0))"

dt['A5']='Campaign start date'; dt['A5'].font=BOLD
c=dt['B5']; c.value=pd.Timestamp('2026-09-07'); c.font=BLUE; c.fill=YFILL; c.number_format='dd-mmm-yyyy'; c.border=BOX
dt['C5']='Dates down the log fill from this cell.'; dt['C5'].font=SUB

dt['A7']='MONTH-TO-DATE PULSE'; dt['A7'].font=BOLD
pulse=[('Days logged',            f'=COUNTIFS($B${LS}:$B${LE},"AG1",$D${LS}:$D${LE},">0")','0','Days with AG1 spend entered'),
       ('MTD spend (Rs)',         f'=SUM($D${LS}:$D${LE})','#,##0',''),
       ('On-pace spend (Rs)',     f'=B8*{ws_cp}!$B$5/{ws_cp}!$B$10','#,##0','Days logged x daily budget'),
       ('Pace',                   '=IF(B10=0,"",B9/B10)','0%','Under 90% = bids are not clearing the auction'),
       ('MTD clicks',             f'=SUM($F${LS}:$F${LE})','#,##0',''),
       ('MTD orders',             f'=SUM($G${LS}:$G${LE})','#,##0',''),
       ('MTD net revenue (Rs)',   f'=SUM($I${LS}:$I${LE})','#,##0','Gross less the assumed return rate — reconcile monthly'),
       ('MTD ROI',                '=IF(B9=0,"",B14/B9)','0.00"x"','The only number that is actually measured'),
       ('Measured account CVR',   '=IF(B12=0,"",B13/B12)','0.00%','Replaces the assumption'),
       ('Planned account CVR',    f'=SUM({ws_cp}!$K$14:$K$19)/SUM({ws_cp}!$J$14:$J$19)','0.00%','Implied by the Control Panel'),
       ('CVR vs plan',            '=IF(B16="","",B16/B17-1)','+0%;-0%','ROI moves with this one-for-one'),
       ('Projected month-end ROI','=IF(OR(B16="",B17=0),"",'+f'{ws_cp}!$E$20*B16/B17)','0.00"x"','Blended target rescaled by measured CVR')]
for i,(lbl,f,fmt,note) in enumerate(pulse):
    r=8+i
    dt.cell(row=r,column=1,value=lbl).font=BLK
    c=dt.cell(row=r,column=2,value=f); c.font=BOLD; c.number_format=fmt; c.border=BOX
    dt.cell(row=r,column=3,value=note).font=SUB
dt.cell(row=20,column=1,value='Verdict').font=BOLD
dt.cell(row=20,column=2,value=f'=IF(B16="","Awaiting data",IF(B19<{ws_cp}!$B$8,"BELOW FLOOR — recut every bid from measured CVR (see Bid Calibration)",IF(B19>{ws_cp}!$B$9,"ABOVE CEILING — raise bids, you are under-buying","INSIDE CORRIDOR — hold")))').font=BOLD

dcols=['Date','AG','Group','Spend (Rs)','Impressions','Clicks','Orders','Gross Rev (Rs)',
       'Net Rev (Rs)','Target Spend','Pace','CTR','Actual CPC','Max CPC','Day CVR','Day ROI',
       'Cum Clicks','Cum Orders','Cum CVR','Cum ROI','DELIVERY CHECK (same day)','DECISION (needs 40 clicks + 10 orders)']
hdr(dt,LH,dcols,[11,7,18,11,12,9,8,13,13,12,8,8,11,10,9,9,11,11,9,9,44,46])
for i in range(DAYS*len(GRP)):
    r=LS+i; g=GRP[i%len(GRP)]
    a=dt.cell(row=r,column=1,value=f'=$B$5+INT((ROW()-{LS})/{len(GRP)})'); a.number_format='dd-mmm'
    dt.cell(row=r,column=2,value=g).font=BLK
    dt.cell(row=r,column=3,value=f'=IFERROR({cp("B",r)},"")').font=BLK
    for col in [4,5,6,7,8]:                                   # input cells
        c=dt.cell(row=r,column=col); c.fill=YFILL; c.font=BLUE
    dt.cell(row=r,column=9, value=f'=IF(H{r}="","",H{r}*(1-{ws_cp}!$B$7))').number_format='#,##0'
    dt.cell(row=r,column=10,value=f'=IFERROR({cp("H",r)},"")').number_format='#,##0'
    dt.cell(row=r,column=11,value=f'=IF(OR(D{r}="",J{r}=0),"",D{r}/J{r})').number_format='0%'
    dt.cell(row=r,column=12,value=f'=IF(OR(E{r}="",E{r}=0),"",F{r}/E{r})').number_format='0.00%'
    dt.cell(row=r,column=13,value=f'=IF(OR(F{r}="",F{r}=0),"",D{r}/F{r})').number_format='#,##0.00'
    dt.cell(row=r,column=14,value=f'=IFERROR({cp("I",r)},"")').number_format='#,##0.00'
    dt.cell(row=r,column=15,value=f'=IF(OR(F{r}="",F{r}=0),"",G{r}/F{r})').number_format='0.00%'
    dt.cell(row=r,column=16,value=f'=IF(OR(D{r}="",D{r}=0),"",I{r}/D{r})').number_format='0.00"x"'
    dt.cell(row=r,column=17,value=f'=IF(D{r}="","",SUMIFS($F${LS}:$F{r},$B${LS}:$B{r},$B{r}))').number_format='#,##0'
    dt.cell(row=r,column=18,value=f'=IF(D{r}="","",SUMIFS($G${LS}:$G{r},$B${LS}:$B{r},$B{r}))').number_format='#,##0'
    dt.cell(row=r,column=19,value=f'=IF(OR(D{r}="",Q{r}=0),"",R{r}/Q{r})').number_format='0.00%'
    dt.cell(row=r,column=20,value=f'=IF(D{r}="","",IFERROR(SUMIFS($I${LS}:$I{r},$B${LS}:$B{r},$B{r})/SUMIFS($D${LS}:$D{r},$B${LS}:$B{r},$B{r}),""))').number_format='0.00"x"'
    dt.cell(row=r,column=21,value=(f'=IF(D{r}="","",'
        f'IF(E{r}=0,"NO IMPRESSIONS — bid under the auction floor, or out of stock in core sizes",'
        f'IF(K{r}<0.6,"UNDERSPENDING — bid is not clearing; raise toward the cap",'
        f'IF(K{r}>1.15,"OVERSPEND — check the daily cap in Partner Portal",'
        f'IF(M{r}>=N{r}*0.98,"BID-CAPPED — paying the max CPC; cannot scale without recutting the bid",'
        f'"Delivering normally")))))')).font=BLK
    dt.cell(row=r,column=22,value=(f'=IF(D{r}="","",'
        f'IF(OR(Q{r}<40,R{r}<10),"COLLECTING — "&Q{r}&" clicks / "&R{r}&" orders (need 40 and 10)",'
        f'IF(T{r}<{ws_cp}!$B$8,"BELOW FLOOR — cut bid 20%, recheck in 7 days",'
        f'IF(T{r}>{ws_cp}!$B$9,"ABOVE CEILING — raise bid 15%, move budget in",'
        f'"ON PLAN — hold, do not touch bids for 2 weeks"))))')).font=BOLD
    for col in range(1,23): dt.cell(row=r,column=col).border=BOX
dt.freeze_panes='D22'

# ---------------- Bid Calibration ----------------
# Closes the loop the bid formula leaves open: the bid is derived FROM assumed CVR, so a CVR
# error passes straight into realised ROI. This tab re-derives every bid from measured CVR.
bc=wb.create_sheet('Bid Calibration')
bc['A1']='BID CALIBRATION — REPLACE THE CVR ASSUMPTION WITH MEASURED DATA'; bc['A1'].font=TITLE
bc['A2']='Max CPC is derived FROM assumed CVR, so if CVR is wrong the bid is wrong and realised ROI misses target one-for-one. Nothing in the plan reveals that. This tab does, from the Daily Tracker.'; bc['A2'].font=SUB
bcols=['AG','Group','Assumed CVR','Clicks to date','Orders to date','Measured CVR','Confidence',
       'Current Max CPC','Corrected Max CPC','Bid change','Realised ROI','Days to reliable','ACTION']
hdr(bc,4,bcols,[7,21,12,13,13,12,14,15,16,11,12,14,42])
sm=summ.set_index('AG')
for i,g in enumerate(GRP):
    r=5+i; cr=14+i
    bc.cell(row=r,column=1,value=g).font=BLK
    bc.cell(row=r,column=2,value=sm.loc[g,'Group']).font=BLK
    bc.cell(row=r,column=3,value=f"={ws_cp}!$F${cr}").number_format='0.00%'
    bc.cell(row=r,column=4,value=f"=SUMIFS('Daily Tracker'!$F${LS}:$F${LE},'Daily Tracker'!$B${LS}:$B${LE},$A{r})").number_format='#,##0'
    bc.cell(row=r,column=5,value=f"=SUMIFS('Daily Tracker'!$G${LS}:$G${LE},'Daily Tracker'!$B${LS}:$B${LE},$A{r})").number_format='#,##0'
    bc.cell(row=r,column=6,value=f'=IF(D{r}=0,"",E{r}/D{r})').number_format='0.00%'
    bc.cell(row=r,column=7,value=f'=IF(E{r}>=30,"RELIABLE",IF(E{r}>=10,"DIRECTIONAL",IF(E{r}>0,"TOO EARLY","NO DATA")))').font=BOLD
    bc.cell(row=r,column=8,value=f"={ws_cp}!$I${cr}").number_format='#,##0.00'
    bc.cell(row=r,column=9,value=f'=IF(F{r}="","",{ws_cp}!$B$6*F{r}*(1-{ws_cp}!$B$7)/{ws_cp}!$E${cr})').number_format='#,##0.00'
    bc.cell(row=r,column=10,value=f'=IF(OR(I{r}="",H{r}=0),"",I{r}/H{r}-1)').number_format='+0%;-0%'
    bc.cell(row=r,column=11,value=f'=IF(F{r}="","",{ws_cp}!$E${cr}*F{r}/C{r})').number_format='0.00"x"'
    bc.cell(row=r,column=12,value=round(30/(sm.loc[g,'Monthly']/30/sm.loc[g,'MaxCPC']*sm.loc[g,'CVR']),1)).number_format='0.0'
    bc.cell(row=r,column=13,value=(f'=IF(E{r}=0,"No data yet — log spend in Daily Tracker",'
        f'IF(E{r}<10,"Keep collecting — "&E{r}&" of 10 orders",'
        f'IF(ABS(J{r})<0.1,"Assumption holds — leave the bid alone",'
        f'IF(E{r}<30,"DIRECTIONAL — move the bid halfway to the corrected figure",'
        f'"RELIABLE — set Control Panel CVR to the measured figure"))))')).font=BOLD
    for col in range(1,14): bc.cell(row=r,column=col).border=BOX
bc.cell(row=11,column=1,value='HOW TO READ THIS').font=BOLD
for i,t in enumerate([
 'Days to reliable = days of planned spend before a group accumulates 30 orders. AG1 8.4, AG2 12.0, AG4 23.6, AG3 48.5, AG5 137.5.',
 'AG3 and AG5 cannot produce a trustworthy CVR inside a month at their budgets. Judge them on clicks and CTR, not ROI, or consolidate their budget.',
 'Realised ROI = target ROI x (measured CVR / assumed CVR). This is the number the projection cannot show you.',
 'Corrected Max CPC = ASP x measured CVR x (1 - return rate) / target ROI. Same formula, real input.',
 'When confidence reads RELIABLE, type the measured CVR into Control Panel column F. Every bid, budget and projection reprices from it.']):
    bc.cell(row=12+i,column=1,value=t).font=SUB

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
