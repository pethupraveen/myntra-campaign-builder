# Strategy one-pager & weekly SOP

## Why the budget concentrates

₹15,000 a month is ₹500 a day. Spread evenly over 4,382 styles that is 11 paise per style per day —
not enough to win a single auction. Spread over 152 styles it is ₹3.29 a day each, roughly one to
two clicks. That is thin but it is real, and Myntra's auction will naturally push the budget toward
the styles that convert.

So the first decision is not *what to bid*. It is *what not to advertise*. Three quarters of the
catalogue is out of the plan on purpose.

The second decision is made for us. Myntra rejects an ad group funded under **₹2,500 a month** and a
campaign under **₹250 a day**, so ₹15,000 buys at most five ad groups (5 × ₹2,500 = ₹12,500) no matter
how the strategy would prefer to slice it. That floor pins AG3, AG4 and AG5 at ₹2,500 each and leaves
₹7,500 to divide between the two strongest groups.

## How each style was scored

- **Organic per day** — organic impressions divided by days live. An older style with 2,000
  impressions is weaker than a two-month-old style with the same number. This removes the age
  advantage.
- **Ad saturation** — paid impressions as a share of total. High saturation means visibility was
  bought, not earned.
- **Demand Score** — 50% reach percentile, 35% velocity percentile, 15% freshness. Styles live
  30–180 days score highest on freshness: proven enough to trust, current enough to sell.
- **Opportunity Score** — Demand Score discounted by ad saturation. It surfaces styles with real
  organic pull that have never been paid for. Those are the cheapest wins available.

## Why the ROI ladder is a ladder

A single 15.5x target across every group would starve discovery: new styles have no conversion
history, so they cannot clear a high bar and would never get funded. A single 5.5x target would
leave money on the table with the proven winners. So the groups sit at different rungs — Hero Scale
at 14x, Rising Stars at 10.5x, Steady Volume at 8x, New Launch at 6x, Retest at the 5.5x floor — and
the budget-weighted blend lands at **9.40x**, comfortably inside the corridor with room to absorb a
bad week. It would be 10.29x if the shares were free; the ₹2,500 ad-group floor forces ₹1,750 of extra
spend into the 5.5x retest group and costs the blend most of that difference.

## Scale and cut rules

| When | Then |
|---|---|
| ROI > 15.5x | Raise the bid 15% and move budget in from the weakest funded group. You are leaving volume on the table. |
| ROI 11x – 15.5x | Hold. Consider promoting the top two queued styles in that group if it is spending its full budget daily. |
| ROI 5.5x – 11x | On plan. Leave bids alone for at least two weeks — a style needs ~40 clicks before its conversion rate means anything. |
| ROI 3.5x – 5.5x | Cut the bid 20%. Recheck after seven days. If the style has spent >₹150 with zero orders, pause it regardless of ROI. |
| ROI < 3.5x for 2 weeks | Pause the style. Promote the highest-ranked queued style in the same ad group. Log the pause — three pauses in one group means the group's CVR assumption is wrong, not the styles. |
| Zero impressions | Not a performance problem. The bid is below the auction floor for that category, or the style is out of stock in core sizes. Check stock first, then raise the bid to the group ceiling. |

## The daily loop — about two minutes

Track **by ad group, never by style.** This is not a preference, it is arithmetic:

| Unit | Clicks/day | Orders/day | Readable daily? |
|---|---|---|---|
| One style | 1.22 – 3.31 | 0.03 – 0.07 | No. One order swings its ROI by 300%. |
| AG1 Hero Scale | 63.9 | 2.9 | Yes |
| AG2 Rising Stars | 56.0 | 2.0 | Yes |
| AG4 Steady Volume | 36.5 | 1.1 | Yes |
| AG5 Retest | 33.1 | 0.7 | Clicks yes, orders no |
| AG3 New Launch | 30.5 | 0.8 | Clicks yes, orders no |

A style needs ~40 clicks before its conversion rate means anything; at roughly 1.4 clicks a day that
is about four weeks. A group clears 40 clicks in well under a day to a day and a half. So the group
is the smallest unit that produces a daily signal.

1. Open Partner Portal, pull yesterday at ad-group level: spend, impressions, clicks, orders, gross revenue.
2. Type five rows into `Daily Tracker`. Only the yellow columns.
3. Open `Daily Action Plan`, put yesterday's date in `B4`, and do what the `DO FIRST` line says.

Once a week, paste the whole log into the dashboard's **Performance** tab. The workbook tells you
about one day; that tab shows the same five groups against their targets with the history behind
them — which is where a drift you cannot see day to day becomes obvious.

### What a day can and cannot tell you

The plan separates two kinds of reading, and mixing them is the mistake the weekly rules used to
allow.

**Priorities 1–4 — delivery. Valid immediately, because they are mechanical facts, not statistics:**

| Reading | Meaning | Fix today |
|---|---|---|
| Zero impressions | Bid is under the category auction floor, or core sizes are out of stock | Check stock, then raise the bid to the group ceiling |
| Spend < 60% of daily target | Bids are not clearing auctions | Raise bid toward the cap |
| Spend > 115% of target | Daily cap is set wrong in Partner Portal | Correct the cap |
| Actual CPC pinned at Max CPC | You are bid-constrained, not budget-constrained | Nothing until the bid is recut from measured CVR |

Underspending is the failure mode to watch. At a ₹2.02 bid the plan assumes it wins auctions; if it
does not, the money simply never leaves the account and the whole ROI question is moot.

**Priorities 5–6 — performance. Gated.** They stay hidden until the group has **40 cumulative clicks
and 10 cumulative orders**; until then the plan reads `COLLECTING` and shows the running count.
Acting on day-3 ROI is acting on noise.

A delivery fault always outranks a bid decision. A group spending 40% of target has no ROI worth
reading, and recutting its bid would fix the wrong thing.

### Returns lag

`Net Rev` applies the 30% return-rate assumption to the same day's gross. Real returns land 7–21
days later, so the daily figure is an estimate and the first three weeks read optimistically.
Reconcile once a month against the actual returns report and correct Control Panel B7.

## The weekly loop — about 40 minutes, every Monday

1. **Pull the numbers.** Export last week's style-level report from Partner Portal. Paste spend,
   impressions, clicks, orders and revenue into the Weekly Tracker tab of the workbook. ROI, CPC and
   the action call compute themselves.
2. **Read the action column.** Sort by ACTION. Act on BELOW FLOOR and ABOVE CEILING first — those two
   are where the money is. Ignore anything with fewer than 40 clicks; it has not earned an opinion yet.
3. **Swap the losers.** Pause what the rules say to pause. For each pause, promote the top queued
   style from the same group and give it the same budget. The roster stays at 152 — that is what keeps
   per-style spend meaningful.
4. **Rebalance between groups.** Once a month, not weekly. Move up to 20% of budget from the
   lowest-ROI funded group to the highest. Re-check that the blended figure is still inside 5.5x–15.5x
   before saving.
5. **Re-score the catalogue.** Every 8 weeks, re-run the pipeline on a fresh impressions export.
   Scores shift as styles age and new ones go live — roughly 15% of the roster turns over each cycle.

## What to watch out for

- **Returns eat ROI silently.** Myntra reports revenue gross. At a 30% return rate a reported 8x is a
  real 5.6x — right at the floor. Always subtract returns before judging a style.
- **Do not judge a style on one week.** At ₹3 a day a style gets ~30 clicks a month. One order swings
  its ROI by 300%. Two weeks minimum, 40 clicks minimum.
- **Stock-outs look like ad failure.** A style that stops converting is often just out of M and L.
  Check inventory before cutting the bid.
- **The excluded 1,955 are not dead.** They score low because their listings are not earning organic
  traffic. Better images, keyword-rich titles and competitive pricing move them up the score without a
  rupee of ad spend. Re-score them after fixing a batch.

## Still missing from this plan

Three inputs would sharpen it materially: **selling price per style** (turns one blended bid per group
into a bid per style), **historical conversion rate** (replaces the CVR assumptions with real numbers),
and **category** (auction floors differ enormously between, say, kurtas and footwear). Style ID → model
name mapping would make the roster readable.
