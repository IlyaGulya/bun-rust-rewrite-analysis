# Classification and adoption through 30 October 2026

The main report now opens with the full **November 2025 → October 30, 2026** timeline. The old August-only charts are in an explicitly labelled, collapsed historical appendix. Current classification and adoption charts appear first, followed by post-stable follow-up.

## What the provisional title classifier shows

| Title signal | Before: 1,802 potential reports | After: 2,389 potential reports |
| --- | ---: | ---: |
| HTTP / network | 162 (8.99%) | 353 (14.78%) |
| Test runner | 37 (2.05%) | 176 (7.37%) |
| Package manager | 152 (8.44%) | 135 (5.65%) |
| Crash / fatal signal | 418 (23.20%) | 195 (8.16%) |
| No component title signal | 1,110 (61.60%) | 1,154 (48.30%) |

These are **exploratory text signals**, not counts of confirmed subsystem defects. They are multi-label and overlap. A title such as “crash report peak” can produce a false positive; missing tags are not negative evidence. The large unclassified share and changing specificity of issue titles prevent a claim that actual crash incidence fell or network quality worsened. The [36-report spot check](CLASSIFICATION-AUDIT.md) covers only reports with some signal and does not estimate recall or overall accuracy.

The classifier applies the same regexes to titles in both periods. Labels are used only for the inherited potential-bug exclusion filter; unequal triage coverage remains a limitation. Separate title-plus-bounded-body counts are shown in the report's sensitivity table. Both periods use at most 2,500 body characters, with fenced code and template prompts removed; incidental mentions can remain. Classification stores rule-match evidence and bounded excerpts per issue in [data/classified.jsonl](data/classified.jsonl). Baseline text/labels were observed on August 10, post-merge on October 30. These are arrival-time periods, not verified Zig/Rust build assignments.

## What adoption adds

Daily npm downloads rose from **171,648/day in April** to **533,390/day over October 1–28**, approximately 3.11×. This supports interpreting report counts alongside changing distribution activity, but does not measure active-user growth. All values derive from the [saved npm response](data/popularity-npm-raw.json); [sources and limitations](POPULARITY-SOURCES.md) describe the endpoints.

| Common complete UTC calendar weeks | Weeks | Potential reports | npm `bun` downloads | Reports per million npm requests |
| --- | ---: | ---: | ---: | ---: |
| Before merge | 25 | 1,678 | 22,569,677 | 74.35 |
| After merge | 24 | 2,378 | 70,795,178 | 33.59 |
| Since stable release (subset of after) | 10 | 1,373 | 35,842,116 | 38.31 |

The pooled ratio is total reports divided by total downloads, not the mean of weekly ratios. We exclude partial and non-overlapping weeks. The initial issue window starts November 13 at 08:09:34 UTC, so its first calendar week is partial. The final issue week starts October 29 and is partial; download data is published only through October 28. Calendar weeks start Thursday at midnight UTC, while the merge/stable events occur later in their boundary day; those daily buckets can mix a few hours across events.

**The denominator and numerator describe different populations.** Reports cover all installation channels and Bun versions, while npm requests cover one channel, all versions, repeat installations and automation. Changes in CI or channel share can lower this ratio with no improvement in defect risk. Do not call it bugs per user, quality improvement or a causal Rust effect. Downloading platform packages can accompany downloading `bun`, so we do not add their counts. GitHub cumulative asset counters are a separate dated table, not historical daily observations.

Weekly GitHub star history is shown as interest alongside this analysis. GitHub currently reports 96,468 stars. The current week is partial; star-week boundaries are not guaranteed to be UTC. We do not use stars as a user-exposure denominator or infer a historical cumulative total from today's count.

## Reproduction

- `pnpm run rebuild`: rebuild the report from committed inputs, without network.
- `pnpm run refresh`: refresh issues, npm and star history, then rebuild. Current repository/release-asset counter snapshots are dated separately; this command does not advance their observation timestamp.
- `python3 part3/popularity.py`: reassemble popularity payload from saved responses.
- `python3 part3/verify.py`: independently check classification counts and download alignment.
- `python3 part2/verify.py`: validate refreshed follow-up data.
- `cd scripts && python3 09-verify.py`: validate the frozen original report.

Files: `classify.py` defines the versioned taxonomy and exports classifications; `build.py` joins complete weeks and renders the current report before the archive; `block.html` contains the interactive controls and charts. Data sources, timestamps, counts and formulas are saved under `data/`. The current HTML includes its data and chart libraries and can be opened offline.

## Daily type stacks by reported version

The first chart now combines version-aware type stacks and npm downloads on one canvas. It supports grouped bars for the four most-reported single versions, a single-version filter, and an all-version aggregate. Every bar is one UTC issue-opening day, through October 30. Controls switch symptoms/components and counts/percentages. Types are exclusive in this chart: one title signal keeps its class, several become `Multiple type signals`, none become `No title signal`. Thus stacked heights equal issue counts. The earlier multi-label comparison remains separate.

`versions.py` reads the bounded issue excerpts, preferring the issue template's Bun version field over explicit adjacent Bun version strings. It never treats a bare library semver as Bun. Base versions are checked against saved official releases because users sometimes put extension, editor or kernel versions in the Bun template field. Unrecognised or unreleased bases remain unknown, so novel canary bases can be missed. Rejected candidates are retained for audit. Several reported versions are grouped separately rather than duplicated across panels; absent versions are unknown. Canary/debug/dev suffixes are retained while build IDs are grouped. A plain `1.4.0` does not establish a release channel. The selected version is what the reporter states, not a confirmed affected version; old versions can receive reports after a new release.

`data/versions.jsonl` retains per-issue version candidates, source/evidence and exclusive chart classes. `data/version-daily.json` holds the daily counts. Run `python3 part3/verify_versions.py` to check extraction edge cases and verify that every report enters each chart exactly once.

## Combined growth comparison

The daily chart replaces the former separate download-overlay and ratio charts. Its default view stacks exclusive problem types and overlays npm download growth on one scale: each series is divided by its own pre-merge daily mean and multiplied by 100. Controls retain raw counts with a labelled download axis, per-million ratios and composition percentages. Version comparisons use grouped stacks within each day on one canvas; filtered numerators still use all-version npm downloads.

Trailing seven-day smoothing uses complete calendar windows. Rate mode uses the ratio of sums across that window. Counts use daily means; growth mode divides those means by the common selected-cohort baseline. In grouped-version mode the report baseline is pooled over the selected versions, so the grouped contributions add to the selected-cohort index. Download indices have their own pre-merge mean. With no report baseline, the report index is undefined rather than zero. The separate raw-count mode remains usable for recent versions.

The current full-day comparison includes 181 paired pre-merge days (November 14–May 13) and 167 post-merge days (May 15–October 28). It excludes the partial first/last report days, the merge day from the summary, and unpublished downloads. Mean reports/day rise 9.79 → 14.12 (1.44×), mean npm requests/day 127,502 → 422,401 (3.31×), and the pooled ratio falls 76.78 → 33.43 reports per million requests (−56.5%). This is descriptive evidence that reports grew more slowly than this npm proxy, not a defect-risk or active-installation estimate. These complete-day figures differ slightly from the older complete-week table above because their inclusion windows differ. The summary covers the full paired window, independently of chart zoom or hidden legend series.

`combined-series.js` is the shared, pure calculation module used directly by the browser and tested by `node part3/combined-series.test.cjs`. It checks paired dates, missing/zero denominators, partial days, smoothing and baseline indices.

## Crash/leak rates and a separate relative-growth graph

[The crash/leak comparison](SAFETY-2026-10-30.md) distinguishes explicit memory retention from broad memory/OOM keywords, exports per-issue evidence, and compares both primary title signals and a bounded-body sensitivity variant. The report now also has a separate line chart for report-index / npm-download-index, with a fixed baseline of 1 and selectable all/crash/leak/memory signals. Both plots use the same complete-day exposure rules as the combined plot. `safety.py` builds the analysis; `verify_safety.py` checks classification edge cases and denominators. The shared `CombinedSeries.growthRatio` calculation is tested directly.
