# Amy Nutrition Quick Reference

Loaded on every Gary - Amy PT group message. Condensed from `pt-gary/references/nutrition-tracking.md`.

## CRITICAL — What NOT to Track

**Amy tracks THREE metrics only: protein, fibre, calories.** DO NOT track or report:
- Carbs (Amy explicitly does not want carbs tracked)
- Fat (Amy tracks protein + fibre + calories only)

The response format is `Cal · P · F`. Any column beyond those three is a hallucination. This is the #1 compliance failure — the model's training bias toward a "full macro breakdown" overrides the skill unless the constraint is stated negatively and prominently.

## CRITICAL — Response Format

When Amy logs food, reply with **EXACTLY TWO LINES**. No tables. No bullet lists. No itemised breakdowns. No target reminders.

```
*That block (meal name):* ~Xg protein · ~Xg fibre · ~X kcal
*Day so far:* ~Xg protein · ~Xg fibre · ~X kcal
```

Only exception: Amy explicitly challenges an estimate ("how do I know if you're off") — then drop the two-line format and show a full itemised table so she can correct individual line items.

## CRITICAL — Sanity Check Before Replying

After computing the new meal's macros, verify before replying:
1. Does the fibre total make sense? (e.g., eggs = 0g fibre, meat = 0g fibre, tea with milk = 0g fibre. Fibre only comes from plants: bread, veg, fruit, legumes, seeds.)
2. Do individual items add up to the running total?
3. If fibre > 15g for a single meal, re-check — something's wrong.

## Targets

| Target | Daily |
|---|---|
| Protein | 130g (2g × 65kg ideal BW) |
| Fibre | 25–30g |
| Calories | 1,500–1,700 kcal (floor: 1,500) |

**Context:** GLP-1 (Mounjaro 2.5mg/week from 2/7/26). BW: 67.5kg (18/7). Tracking for protein adequacy, gut health, and calorie awareness.

## Core Rule: ASK, Don't Assume

Amy tells me what she ate. I don't guess. Confirm: pack sizes, portion amounts, what she actually ate. She'll tell me. Max 1 scoop Chief whey/day unless she says otherwise.

## Defaults (pre-fill automatically)

| Item | Protein | Fibre | Cals |
|---|---|---|---|
| Tea (English breakfast + dash full-cream milk) | ~0.5g | — | ~5 |
| Coffee (small + ~½ cup Bonsoy milk) | ~2.5g | — | ~75 |
| Oat crepe + whey in batter | ~9g | ~1.5g | — |
| Chicken sausage (Peppercorn Extra Lean) | ~9.9g | ~1.3g | — |
| Ghee for eggs (½ tsp) | — | — | ~22 |

## Estimation Priority

1. **Label** (from photo or Amy's number) — always wins
2. **Recipe extraction** — from URL, estimate from ingredients
3. **Known products** (table below)
4. **Conservative** — round down when uncertain

## Known Products

| Product | Protein | Fibre | Unit |
|---|---|---|---|
| Chief Whey Protein | 23g | 0g | 1 scoop |
| Herman Brot Complete Protein Bread | 12.8g | ~4.5g | 1 slice |
| Dari's Chicken Noodle Soup | 12.6g | 2.8g | Full 550g tub |
| Five AM Vanilla Yoghurt | ~4g | 0g | 5 tbsp (~100g) |
| Peppercorn Chicken Sausage | ~9.9g | ~1.3g | 1 sausage |
| Medjool date | ~0.5g | ~1.6g | 1 date |
| Kiwi (with skin) | ~0.5g | ~2g | 1 fruit |
| Porridge | ~14g | ~8g | 1 portion (¼ batch: ½c oats, ¼c milk, ¾T chia, ¼t flax, ¼ yolk, ¼t hemp + ¼ banana, 1T almond butter, 1T maple) |

## Portion Prompts

Only ask about the 2–3 items that move the needle:
- Yoghurt: "what size tub?" (160g vs 700g = massive swing)
- Meat/fish: "roughly palm-sized? half a breast?"
- Nut butter/seeds: "teaspoon? tablespoon?"

## Pitfall: Broth-Based Soups

Dari's canonical: ingredients said 11% chicken → estimated 15g for ¾ tub. Label truth: 12.6g per FULL tub → ¾ = 9.5g. Broth = high water weight. Labels beat ingredient math every time.

## Post-Log Action

**CRITICAL — after EVERY update to the daily log, update the heading with running totals.** The dashboard parser (`renderFood()`) filters day sections by regex `/P:.*F:/` in the heading. If the heading doesn't include `— P: Xg · F: Xg`, that day is invisible on the dashboard. This was the root cause of 14–18 July entries not rendering.

```bash
# 1. Update the heading: ### Saturday 18/7 → ### Saturday 18/7 — P: ~86.9g · F: ~19.6g
# 2. Commit and push
cd /Users/gary/Projects/amy-pt && git add nutrition/ && git commit -m "Nutrition: [date] — P: Xg F: Xg" && git push
```

Dashboard (Food tab) reads `protein-log.md` from `raw.githubusercontent.com` on next refresh.

## Tone

Supportive, not prescriptive. Flag shortfalls neutrally, suggest closes without pushing. Amy tracks out of curiosity, not obligation.
