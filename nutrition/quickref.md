# Amy Nutrition Quick Reference

Loaded on every Gary - Amy PT group message. Condensed from `pt-gary/references/nutrition-tracking.md`.

## Targets

| Target | Daily |
|---|---|
| Protein | 130g (2g × 65kg ideal BW) |
| Fibre | 25–30g |

**Context:** GLP-1 (Mounjaro 2.5mg/week from 2/7/26). Tracking for protein adequacy and gut health.

## Core Rule: ASK, Don't Assume

Amy tells me what she ate. I don't guess. Confirm: pack sizes, portion amounts, what she actually ate. She'll tell me. Max 1 scoop Chief whey/day unless she says otherwise.

## Defaults (pre-fill automatically)

| Item | Protein | Fibre |
|---|---|---|
| Tea (English breakfast + dash lactose-free milk) | ~0.5g | — |
| Coffee (small + ~½ cup Bonsoy milk) | ~2.5g | — |
| Oat crepe + whey in batter | ~9g | ~1.5g |
| Chicken sausage (Peppercorn Extra Lean) | ~9.9g | ~1.3g |

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

```bash
cd /Users/gary/Projects/amy-pt && git add nutrition/ && git commit -m "Nutrition: [date] — P: Xg F: Xg" && git push
```

Dashboard (Food tab) reads `protein-log.md` from GitHub Pages on next refresh.

## Tone

Supportive, not prescriptive. Flag shortfalls neutrally, suggest closes without pushing. Amy tracks out of curiosity, not obligation.
