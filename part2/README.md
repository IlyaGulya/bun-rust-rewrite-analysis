# Releases and fixes after stable 1.4.0

Read the [30 October findings](UPDATE-2026-10-30.md), [source checks](SOURCES-2026-10-30.md), and [snapshot details](data/snapshot.json).

The original report ends on 10 August 2026. At that time, the Rust build was available only on canary. Stable Bun 1.4.0 was released on 20 August, 98 calendar days after the merge. This folder adds later reports and releases. It does not change the original source data.

## Build and check

```bash
pnpm run refresh
pnpm run rebuild
python3 part2/verify.py
```

`refresh` collects new data and builds the report. `rebuild` uses saved data without network access. It can use the committed issue records when the ignored full-response cache is absent. Both commands replace the section between the `part2:start` and `part2:end` comments in `index.html`. Repeated builds do not add duplicate sections.

The collection timestamp changes only when data is collected. Editing a cache file does not change that timestamp.

GitHub search is limited to 1,000 results per query. The collector splits the dates into monthly ranges. Unauthenticated requests are spaced seven seconds apart.

## Files

| File | Purpose |
| --- | --- |
| `update.py` | Collect issues, apply rules, calculate totals, and insert the section |
| `block.html` | Section text, layout, and chart code |
| `echarts.js` | Chart components bundled during the build |
| `data/issues.jsonl` | Committed issue records |
| `data/series.js` | Committed chart data |
| `data/releases.json` | Saved stable releases |
| `data/snapshot.json` | Collection time and search ranges |
| `data/raw.json` | Full API response; ignored by Git |

When the full cache is present, `python3 part2/update.py --no-fetch` applies the text rules again. When it is absent, the build uses saved flags from the committed records.

## Charts

The build includes ECharts, uPlot, and their data in `index.html`. The current report works offline.

The report-count chart uses [ECharts](https://echarts.apache.org/). Drag the slider to choose dates. Scroll to zoom. Drag inside the plot to move the visible range. The chart chooses calendar days, weeks, or months so that no more than 60 bars are visible. Partial periods have narrower bars. Their tooltips show the covered days. A bar stays visible when only part of its date range is in view.

The word-mention chart uses [uPlot](https://github.com/leeoniya/uPlot). Hover over a line to highlight it. Drag to zoom, scroll to scale, and double-click to reset. Long cumulative series use fewer plotted points. The code resets both scales after it changes the sample, then restores the selected dates.

Release lines stay visible when labels would overlap. Labels return when zoom gives them enough space. ECharts uses `markLine`; uPlot uses labels above its canvas. uPlot labels use three rows, an 11px line height, and a 12px row spacing. Check a long date range after changes to this logic.

## Rules and limits

- Before 20 August, a `1.4.0` mention can indicate canary. After stable 1.4.0, that text alone cannot identify the channel. The canary rule therefore has a date limit.
- Crash, hang, panic, and memory counts use word matches. A mention does not confirm the reported problem or its cause. One issue can match several words.
- GitHub labels change over time. Counting only issues with a crash label would also measure how often maintainers add that label.
- Open-issue history is estimated from creation and latest closure dates. The snapshot cannot recover earlier reopen and reclose events. This estimate covers issues opened after the merge, not all issues in the repository.
- Before-merge records come from the original `data/*.jsonl` files. Their observed states stay fixed. Release dates start with `data/releases.tsv` and add later saved releases.
