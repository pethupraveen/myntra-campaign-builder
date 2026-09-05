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
gcols=['Ad Group','Group Name','Active Styles','Budget %','Target ROI (ROAS)','Assumed CVR','Monthly Budget (Rs)','Daily Budget (Rs)','Max CPC Bid (Rs)','Est. Clicks/mo','Est. Orders/mo','Est. Net Revenue (Rs)','Portal Check']
hdr(ws,13,gcols,[11,24,13,10,15,12,17,16,15,14,14,19,46])
ws.freeze_panes=None
# hdr() freezes panes; clearing that drops the <pane> but leaves a pane-bound <selection>
# behind, which Excel rejects outright as a corrupt file. Drop the stale selection too.
ws.sheet_view.selection=[]
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
    ws.cell(row=r,column=13,value=(f'=IF(G{r}=0,"not funded",'
        f'IF(G{r}<$B$35,"BELOW MIN - Myntra will reject this ad group","OK"))')).font=BOLD
    for col in range(1,14): ws.cell(row=r,column=col).border=BOX
    r+=1
tot=r
ws.cell(row=tot,column=2,value='PORTFOLIO TOTAL').font=BOLD
for col,f,fmt in [(3,f'=SUM(C14:C{r-1})','0'),(4,f'=SUM(D14:D{r-1})','0%'),(7,f'=SUM(G14:G{r-1})','#,##0'),
                  (8,f'=SUM(H14:H{r-1})','#,##0.0'),(10,f'=SUM(J14:J{r-1})','#,##0'),
                  (11,f'=SUM(K14:K{r-1})','#,##0.0'),(12,f'=SUM(L14:L{r-1})','#,##0')]:
    c=ws.cell(row=tot,column=col,value=f); c.font=BOLD; c.number_format=fmt; c.border=BOX
c=ws.cell(row=tot,column=5,value=f'=IF(G{tot}=0,0,L{tot}/G{tot})'); c.font=BOLD; c.number_format='0.00"x"'; c.border=BOX
c=ws.cell(row=tot,column=13,value='=IF($B$5/$B$10<$B$36,"CAMPAIGN DAILY BELOW MIN - Myntra will reject the campaign","OK")')
c.font=BOLD; c.border=BOX

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

# Portal floors. These are not preferences - Partner Portal refuses a setup that breaks them,
# so a plan that ignores them cannot be entered at all. src/model.py allocates against them.
ws.cell(row=tot+14,column=1,value='PORTAL MINIMUMS — Myntra rejects any setup under these').font=BOLD
for i,(lbl,val,fmt,note) in enumerate([
        ('Min ad group budget (Rs/month)',2500,'#,##0','Every funded ad group must clear this'),
        ('Min campaign budget (Rs/day)',250,'#,##0','Monthly Budget / Days in Month must clear this')]):
    r2=tot+15+i
    ws.cell(row=r2,column=1,value=lbl).font=BLK
    c=ws.cell(row=r2,column=2,value=val); c.font=BLUE; c.fill=YFILL; c.number_format=fmt; c.border=BOX
    ws.cell(row=r2,column=3,value=note).font=SUB

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
LH=7; LS=8; LE=LS+DAYS*len(GRP)-1                         # log header / first row / last row
CP="'Control Panel'"
dt=wb.create_sheet('Daily Tracker')
dt['A1']='DAILY TRACKER — INPUT'; dt['A1'].font=TITLE
dt['A2']='Five rows a day, about two minutes. Fill only the yellow columns; everything from column I rightwards computes itself.'; dt['A2'].font=SUB
dt['A3']='Read the day back on the Daily Action Plan tab — this tab is for entry, that tab tells you what to do.'; dt['A3'].font=SUB

dt['A5']='Start date'; dt['A5'].font=BOLD
c=dt['B5']; c.value=pd.Timestamp('2026-09-07'); c.font=BLUE; c.fill=YFILL; c.number_format='dd-mmm-yyyy'; c.border=BOX
dt['C5']='Dates down the log fill from this cell.'; dt['C5'].font=SUB

def cpq(col,row):  return f"INDEX({CP}!${col}$14:${col}$19,MATCH($B{row},{CP}!$A$14:$A$19,0))"

dcols=['Date','AG','Group','Spend (Rs)','Impressions','Clicks','Orders','Gross Rev (Rs)',
       'Net Rev (Rs)','Target Spend','Pace','CTR','Actual CPC','Max CPC','Day CVR','Day ROI',
       'Cum Clicks','Cum Orders','Cum CVR','Cum ROI','Flag']
# column B is 13 wide, not 7: it holds the AG code in the log but the start date in B5
hdr(dt,LH,dcols,[11,13,20,11,12,9,8,13,13,12,8,8,11,10,9,9,11,11,9,9,14])
for i in range(DAYS*len(GRP)):
    r=LS+i; g=GRP[i%len(GRP)]
    a=dt.cell(row=r,column=1,value=f'=$B$5+INT((ROW()-{LS})/{len(GRP)})'); a.number_format='dd-mmm'
    dt.cell(row=r,column=2,value=g).font=BLK
    dt.cell(row=r,column=3,value=f'=IFERROR({cpq("B",r)},"")').font=BLK
    for col in [4,5,6,7,8]:                                   # input cells
        c=dt.cell(row=r,column=col); c.fill=YFILL; c.font=BLUE
    dt.cell(row=r,column=9, value=f'=IF(H{r}="","",H{r}*(1-{CP}!$B$7))').number_format='#,##0'
    dt.cell(row=r,column=10,value=f'=IFERROR({cpq("H",r)},"")').number_format='#,##0'
    dt.cell(row=r,column=11,value=f'=IF(OR(D{r}="",J{r}=0),"",D{r}/J{r})').number_format='0%'
    dt.cell(row=r,column=12,value=f'=IF(OR(E{r}="",E{r}=0),"",F{r}/E{r})').number_format='0.00%'
    dt.cell(row=r,column=13,value=f'=IF(OR(F{r}="",F{r}=0),"",D{r}/F{r})').number_format='#,##0.00'
    dt.cell(row=r,column=14,value=f'=IFERROR({cpq("I",r)},"")').number_format='#,##0.00'
    dt.cell(row=r,column=15,value=f'=IF(OR(F{r}="",F{r}=0),"",G{r}/F{r})').number_format='0.00%'
    dt.cell(row=r,column=16,value=f'=IF(OR(D{r}="",D{r}=0),"",I{r}/D{r})').number_format='0.00"x"'
    dt.cell(row=r,column=17,value=f'=IF(D{r}="","",SUMIFS($F${LS}:$F{r},$B${LS}:$B{r},$B{r}))').number_format='#,##0'
    dt.cell(row=r,column=18,value=f'=IF(D{r}="","",SUMIFS($G${LS}:$G{r},$B${LS}:$B{r},$B{r}))').number_format='#,##0'
    dt.cell(row=r,column=19,value=f'=IF(OR(D{r}="",Q{r}=0),"",R{r}/Q{r})').number_format='0.00%'
    dt.cell(row=r,column=20,value=f'=IF(D{r}="","",IFERROR(SUMIFS($I${LS}:$I{r},$B${LS}:$B{r},$B{r})/SUMIFS($D${LS}:$D{r},$B${LS}:$B{r},$B{r}),""))').number_format='0.00"x"'
    dt.cell(row=r,column=21,value=(f'=IF(D{r}="","",'                       # short flag; the prose lives on the plan tab
        f'IF(E{r}=0,"NO DELIVERY",IF(K{r}<0.6,"UNDERSPEND",IF(K{r}>1.15,"OVERSPEND",'
        f'IF(M{r}>=N{r}*0.98,"BID-CAPPED","OK")))))')).font=BOLD
    for col in range(1,22): dt.cell(row=r,column=col).border=BOX
dt.freeze_panes='D8'

# ---------------- Daily Action Plan ----------------
# The output side of the tracker: pick a date, get the five groups ranked by urgency and a
# named action for each. The severity code in column A drives both the reading and the action
# text, so the ladder is written once - a delivery fault always outranks a bid decision.
DTD=f"'Daily Tracker'!$A${LS}:$A${LE}"; DTG=f"'Daily Tracker'!$B${LS}:$B${LE}"
DTS=f"'Daily Tracker'!$D${LS}:$D${LE}"; DTI=f"'Daily Tracker'!$E${LS}:$E${LE}"
DTC=f"'Daily Tracker'!$F${LS}:$F${LE}"; DTO=f"'Daily Tracker'!$G${LS}:$G${LE}"
DTN=f"'Daily Tracker'!$I${LS}:$I${LE}"

ap=wb.create_sheet('Daily Action Plan')
ap['A1']='DAILY ACTION PLAN — OUTPUT'; ap['A1'].font=TITLE
ap['A2']='Type a date in B4. This tab reads that day out of the Daily Tracker and tells you what to change today, in priority order.'; ap['A2'].font=SUB
ap['A3']='Priority 1-4 are delivery faults — mechanical, valid the same day. Priority 5-6 are bid decisions, and only appear once the group has 40 clicks and 10 orders.'; ap['A3'].font=SUB

ap['A4']='Plan date'; ap['A4'].font=BOLD
c=ap['B4']; c.value="='Daily Tracker'!$B$5"; c.font=BLUE; c.fill=YFILL; c.number_format='dd-mmm-yyyy'; c.border=BOX
ap['C4']='Defaults to the campaign start date — overwrite it with the day you just logged.'; ap['C4'].font=SUB

ap['A5']='DO FIRST'; ap['A5'].font=BOLD
c=ap['B5']; c.font=BOLD
c.value=('=IF(COUNT($A$9:$A$13)=0,"No data logged for "&TEXT($B$4,"dd-mmm")&" — enter the five rows on the Daily Tracker tab.",'
         'IF(MIN($A$9:$A$13)>=7,"Nothing to fix. Every logged group is delivering — hold all bids.",'
         'INDEX($C$9:$C$13,MATCH(MIN($A$9:$A$13),$A$9:$A$13,0))&": "&INDEX($R$9:$R$13,MATCH(MIN($A$9:$A$13),$A$9:$A$13,0))))')
ap['A6']='Day status'; ap['A6'].font=BOLD
ap['B6']=('="Logged "&COUNT($A$9:$A$13)&" of 5 groups  |  "&COUNTIF($A$9:$A$13,"<5")&" delivery faults to fix today  |  "'
          '&(COUNTIF($A$9:$A$13,5)+COUNTIF($A$9:$A$13,6))&" bid changes due  |  "&COUNTIF($A$9:$A$13,7)&" holding"')

acols=['Priority','AG','Group','Spend (Rs)','Target (Rs)','Pace','Impressions','Clicks','CTR','Orders',
       'Actual CPC','Max CPC','Day ROI','Cum Clicks','Cum Orders','Cum ROI','READING','ACTION FOR TODAY']
hdr(ap,8,acols,[11,13,20,11,11,8,12,9,8,8,11,10,9,11,11,9,58,60])

# The severity ladder, written once: index i of these lists is priority code i+1.
READ=['"Zero impressions — the bid is under the category auction floor, or core sizes are out of stock."',
      '"Spend at "&TEXT(F{r},"0%")&" of target — bids are not clearing auctions."',
      '"Spend at "&TEXT(F{r},"0%")&" of target — the daily cap is set wrong in Partner Portal."',
      '"Actual CPC is pinned at the Max CPC — bid-constrained, not budget-constrained."',
      '"Cumulative ROI "&TEXT(P{r},"0.00")&"x is below the "&TEXT(' + CP + '!$B$8,"0.0")&"x floor on "&N{r}&" clicks / "&O{r}&" orders."',
      '"Cumulative ROI "&TEXT(P{r},"0.00")&"x is above the "&TEXT(' + CP + '!$B$9,"0.0")&"x ceiling on "&N{r}&" clicks / "&O{r}&" orders."',
      'IF(OR(N{r}<40,O{r}<10),"Delivering normally. "&N{r}&" clicks / "&O{r}&" orders — too thin to judge ROI yet.",'
      '"Delivering normally, cumulative ROI "&TEXT(P{r},"0.00")&"x sits inside the corridor.")']
ACT= ['"Check core-size stock first. If it is in stock, raise the bid to the group ceiling today."',
      '"Raise the bid toward the Max CPC cap today. Underspend is the live problem, not ROI."',
      '"Correct this group' + "'" + 's daily cap in Partner Portal today."',
      '"Nothing today. This group cannot scale until the bid is recut from a measured CVR."',
      '"Cut the bid 20% and recheck in 7 days."',
      '"Raise the bid 15% and move budget into this group — you are under-buying it."',
      'IF(OR(N{r}<40,O{r}<10),"COLLECTING — "&N{r}&" clicks / "&O{r}&" orders (needs 40 and 10). Hold the bid.",'
      '"On plan — hold. Do not touch the bid for 2 weeks.")']

sm=summ.set_index('AG')
for i,g in enumerate(GRP):
    r=9+i; cr=14+i
    ap.cell(row=r,column=2,value=g).font=BLK
    ap.cell(row=r,column=3,value=sm.loc[g,'Group']).font=BLK
    ap.cell(row=r,column=1,value=(f'=IF(COUNTIFS({DTD},$B$4,{DTG},$B{r},{DTS},"<>")=0,"",'
        f'IF(G{r}=0,1,IF(F{r}<0.6,2,IF(F{r}>1.15,3,'
        f'IF(AND(K{r}<>"",K{r}>=L{r}*0.98),4,'
        f'IF(OR(N{r}<40,O{r}<10),7,'
        f'IF(P{r}<{CP}!$B$8,5,IF(P{r}>{CP}!$B$9,6,7))))))))')).font=BOLD
    ap.cell(row=r,column=4,value=f'=SUMIFS({DTS},{DTD},$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=5,value=f'={CP}!$H${cr}').number_format='#,##0'
    # Pace repeats the logged test rather than reading $A: the ladder in A reads pace, so
    # pointing pace back at A would make the pair circular.
    ap.cell(row=r,column=6,value=(f'=IF(OR(COUNTIFS({DTD},$B$4,{DTG},$B{r},{DTS},"<>")=0,E{r}=0),"",'
                                  f'D{r}/E{r})')).number_format='0%'
    ap.cell(row=r,column=7,value=f'=SUMIFS({DTI},{DTD},$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=8,value=f'=SUMIFS({DTC},{DTD},$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=9,value=f'=IF(G{r}=0,"",H{r}/G{r})').number_format='0.00%'
    ap.cell(row=r,column=10,value=f'=SUMIFS({DTO},{DTD},$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=11,value=f'=IF(H{r}=0,"",D{r}/H{r})').number_format='#,##0.00'
    ap.cell(row=r,column=12,value=f'={CP}!$I${cr}').number_format='#,##0.00'
    ap.cell(row=r,column=13,value=f'=IF(D{r}=0,"",SUMIFS({DTN},{DTD},$B$4,{DTG},$B{r})/D{r})').number_format='0.00"x"'
    ap.cell(row=r,column=14,value=f'=SUMIFS({DTC},{DTD},"<="&$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=15,value=f'=SUMIFS({DTO},{DTD},"<="&$B$4,{DTG},$B{r})').number_format='#,##0'
    ap.cell(row=r,column=16,value=(f'=IFERROR(SUMIFS({DTN},{DTD},"<="&$B$4,{DTG},$B{r})'
                                   f'/SUMIFS({DTS},{DTD},"<="&$B$4,{DTG},$B{r}),"")')).number_format='0.00"x"'
    rd=','.join(t.format(r=r) for t in READ)
    at=','.join(t.format(r=r) for t in ACT)
    c=ap.cell(row=r,column=17,value=f'=IF($A{r}="","Not logged for this date",CHOOSE($A{r},{rd}))')
    c.font=BLK; c.alignment=Alignment(wrap_text=True,vertical='top')
    c=ap.cell(row=r,column=18,value=f'=IF($A{r}="","Enter this group\'s row on the Daily Tracker",CHOOSE($A{r},{at}))')
    c.font=BOLD; c.alignment=Alignment(wrap_text=True,vertical='top')
    ap.row_dimensions[r].height=44
    for col in range(1,19): ap.cell(row=r,column=col).border=BOX

ap.cell(row=15,column=3,value='DAY TOTAL').font=BOLD
for col,f,fmt in [(4,'=SUM(D9:D13)','#,##0'),(5,'=SUM(E9:E13)','#,##0'),(6,'=IF(E15=0,"",D15/E15)','0%'),
                  (7,'=SUM(G9:G13)','#,##0'),(8,'=SUM(H9:H13)','#,##0'),(10,'=SUM(J9:J13)','#,##0'),
                  (13,f'=IF(D15=0,"",SUMIFS({DTN},{DTD},$B$4)/D15)','0.00"x"')]:
    c=ap.cell(row=15,column=col,value=f); c.font=BOLD; c.number_format=fmt; c.border=BOX

ap.cell(row=17,column=1,value='HOW THE PRIORITY LADDER WORKS').font=BOLD
for i,t in enumerate([
 '1 NO DELIVERY   2 UNDERSPENDING   3 OVERSPEND   4 BID-CAPPED  -  mechanical faults. Same-day facts, not statistics. Fix them the day you see them.',
 '5 BELOW FLOOR   6 ABOVE CEILING  -  bid decisions. Gated behind 40 cumulative clicks and 10 cumulative orders, so no bid moves on a three-day sample.',
 '7 HOLD  -  either still collecting, or delivering inside the ROI corridor. Change nothing.',
 'A delivery fault always outranks a bid decision: a group spending 40% of target has no ROI worth reading, and recutting its bid would fix the wrong thing.',
 'Underspending is the failure mode to watch. At a Rs 2.02 bid the plan assumes it wins auctions; if it does not, the money simply never leaves the account.',
 'Net Rev applies the return-rate assumption to the same day gross. Real returns land 7-21 days later, so the first three weeks read optimistically.']):
    ap.cell(row=18+i,column=1,value=t).font=SUB
ap.freeze_panes='D9'

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
