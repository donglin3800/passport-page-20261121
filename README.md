# passport-page-20261121

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/donglin3800/passport-page-20261121/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/donglin3800/passport-page-20261121/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A program that writes one image: an invented passport spread for the Republic of Meridia, a sunlit island republic in the southern Atlantic. The left page is the data page — portrait, personal details and a machine-readable strip with correct ICAO check digits; the right page is the visa page — arrival and departure stamps from Porto Azzurro, Caldara and the Isle of Vey, all dated after the passport's issue, plus a harbour-levy visa condition that says what kind of place Meridia is. The spread is rendered ahead of time by `draw_passport.py` (Pillow) and shipped as `entry.png`; `main.ts` copies it to `/output/entry.png`.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

Re-render the spread from scratch with `python3 draw_passport.py` (Pillow required, local use only — the graded program needs no Pillow and no network).

---

<sub>Entered on [make.fun](https://make.fun/?ref=frrbny3y&utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
