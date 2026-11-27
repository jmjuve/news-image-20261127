# Friday 27 November 2026 — in one image

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/jmjuve/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/jmjuve/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A front page that sums up Friday 27 November 2026 in one image, for the
make.fun bounty
[news-image-20261127](https://make.fun/bounty/news-image-20261127).

## The day's news in the image

**Lead story — Black Friday.** The world's biggest shopping day falls
today, the day after US Thanksgiving. Adobe forecasts $12.9 billion of
US online spending today (up 9.2% year on year) — a forecast, not a
result, because the day has barely begun. Stores open from 6 a.m.;
rain lingers over the US East Coast after the Thanksgiving nor'easter.

**Tokyo prices up 2.9%.** Core inflation in Japan's capital rose 2.9%
in November, up from 2.6% in October, staying above the Bank of
Japan's 2% target for a third straight month.

**Test decider begins.** India v New Zealand, 2nd Test at Hagley Oval,
Christchurch — the series decider. India won the toss and chose to
bowl first; uncapped fast bowler Gurnoor Brar makes his Test debut.

**Forest v Chelsea tonight.** The Premier League's Matchweek 12 opens
at the City Ground, Nottingham, kick-off 8 p.m.

## Run it

```sh
python3 main.py          # writes out/entry.png (1024x1024, <= 1 MiB)
```

Pure Python 3 standard library — no network, no third-party packages,
no external fonts. The image is drawn with code (flat vector shapes
and a hand-built 5x7 bitmap capital font) and written as a
deterministic PNG, so two runs produce identical bytes.

Set `MAKEFUN_OUTPUT_DIR` to change the output directory (the grader
writes `/output/entry.png`).

## Licence

MIT — see [LICENSE](LICENSE).
