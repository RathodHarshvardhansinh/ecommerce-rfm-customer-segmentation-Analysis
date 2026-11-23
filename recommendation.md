# Which segment to target, and how

This is the one-page business recommendation that goes with the RFM analysis.
Exact customer counts and revenue shares for your run are in
`outputs/segment_summary.csv`.

## What the segments mean

| Segment | Who they are | What to do |
|---|---|---|
| Champions | Bought recently, buy often, spend the most | Reward them. Early access to new products, a loyalty tier, referral offer. No discounts needed, they already buy. |
| Loyal Customers | Regular buyers with decent spend | Upsell and cross-sell. Bundle offers, push them toward Champion level. |
| New / Promising | Recent buyers with only 1-2 orders | Welcome series and a second-purchase nudge. The first repeat order decides if they stay. |
| Can't Lose Them | Used to buy a lot, have gone quiet | Highest priority win-back. Personal outreach and a strong offer, because each one was worth a lot. |
| At Risk | Mid frequency, haven't ordered in a while | Reminder campaign: "we miss you" plus a limited-time discount. |
| Hibernating | Low activity, last order was some time ago | Cheap automated email only. Do not spend heavy budget here. |
| Lost | Very old last order and very few orders | Last attempt email, then stop. Remove from paid campaigns. |

## The segment I would target first

**Can't Lose Them** (with At Risk as the second wave).

Reason: these customers have already proven they spend, so winning them back
is cheaper than finding new buyers, and each one recovered brings back much
more revenue than a Hibernating or Lost customer would. Champions are already
loyal, so extra discounts there mostly just reduce margin.

## Suggested campaign

- **Channel:** email first, WhatsApp / SMS for the top spenders in the segment
- **Offer:** a time-limited discount on the categories they bought most before, valid for 14 days
- **Message:** personal, mention that it has been a while, do not sound like a mass blast
- **Follow up:** one reminder on day 7, then stop
- **Measure:** reactivation rate (how many order again within 30 days), revenue per email sent, and cost of discount vs revenue won back

## How to check it worked

Split the segment randomly. Send the offer to one half and nothing to the
other half. If the offered group reorders clearly more, the campaign is worth
repeating for At Risk.

## Limits of this analysis

- The data is one UK-based online retailer's transactions from 2010-2011, mostly wholesale buyers, so behavior may differ from a normal consumer store.
- RFM only looks at purchase behavior. It does not know product category, returns, or marketing channel.
- Segment cut-offs are quintile based, so they are relative to this customer base.
