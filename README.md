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
| AG1 | Hero Scale           | `HEALTHY` and Demand Score ≥ 78          | 121   | 45   | ₹4,800 (32%) | 14.0x      | ₹2.02    |
| AG2 | Rising Stars         | Demand Score ≥ 78                        | 591   | 42   | ₹4,500 (30%) | 10.5x      | ₹2.16    |
| AG3 | New Launch Incubator | ≤ 120 days live and Demand Score 50–78   | 127   | 25   | ₹1,950 (13%) | 6.0x       | ₹2.73    |
| AG4 | Steady Volume        | Demand Score 45–78                       | 1,535 | 30   | ₹3,000 (20%) | 8.0x       | ₹2.28    |
| AG5 | Ad-Dependent Retest  | Demand Score < 45 with past paid impr.   | 53    | 10   | ₹750 (5%)    | 5.5x       | ₹2.52    |
| AG6 | Dormant — Excluded   | Demand Score < 45, never advertised      | 1,955 | 0    | ₹0           | —          | —        |

¹ at the default ₹899 ASP / 30% return-rate assumption.

Budget-weighted blend: **10.29x** — mid-corridor, with room to absorb a bad week.
Projection: 6,787 clicks, 245 orders, ₹1,54,275 net revenue per month, ₹61 per order.

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
data/                CSV outputs — full scored master, active roster, queue, excluded, group summary
index.html           self-contained HTML performance dashboard (no build step, no dependencies)
output/              Myntra_Campaign_Builder.xlsx — 7 tabs, formula-driven from a Control Panel
docs/                strategy one-pager and weekly optimisation SOP
```

## Running it

```bash
pip install pandas numpy openpyxl
python src/engine.py       # data.csv -> scored.csv
python src/groups.py       # scored.csv -> grouped.csv
python src/model.py        # grouped.csv -> final.csv, summary.csv
python src/build_xlsx.py   # -> Myntra_Campaign_Builder.xlsx
```

Input is a CSV named `data.csv` with columns:
`Style Id, Live Since (DD-MM-YYYY), Organic Impressions, Inorganic Impressions, Total Impressions, Health, Reasons`.

Open `index.html` directly in a browser — it needs no server.

### Live dashboard

`.github/workflows/pages.yml` deploys the dashboard to GitHub Pages on every push to `main`.
Enable it once at **Settings → Pages → Source: GitHub Actions**, and the site goes live at
`https://<your-username>.github.io/myntra-campaign-builder/`.

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
