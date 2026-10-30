# Report types and Bun downloads through 30 October 2026

The [current report](../index.html) covers November 2025 to 30 October 2026. The [original August report](../archive/report-2026-08-10.html) is stored separately.

## Title matches

| Title match | Before: 1,802 possible bug reports | After: 2,389 possible bug reports |
| --- | ---: | ---: |
| HTTP and networks | 162 (8.99%) | 353 (14.78%) |
| Tests | 37 (2.05%) | 176 (7.37%) |
| Package installation | 152 (8.44%) | 135 (5.65%) |
| Crash or fatal signal | 418 (23.20%) | 195 (8.16%) |
| No component title match | 1,110 (61.60%) | 1,154 (48.30%) |

The same text rules apply to both periods. A report can match several types. These counts describe words in reports. They do not confirm a defect, its component, or its cause. For example, “crash report peak” can match the crash rule without describing a crash. No match does not mean no problem.

Many titles name no component. Later titles can also contain more detail. Changes in these shares therefore cannot show that actual crash frequency fell or that network quality became worse. The [36-report review](CLASSIFICATION-AUDIT.md) checks only reports with at least one match. It does not measure how many problems the rules miss.

The separate body text check adds up to 2,500 characters per report. It removes fenced code and template prompts. Other unrelated mentions can remain. [Per-report records](data/classified.jsonl) keep the matches and excerpts. Before-merge text and labels were observed on 10 August. After-merge text and labels were observed on 30 October. These are report-date groups. They do not prove which language implementation was used.

## Downloads and stars

Mean daily npm requests rose from **171,648 in April** to **533,390 over 1–28 October**, about 3.11 times. These are requests for the `bun` package. They include repeated downloads and automated builds. They do not count active users. See the [saved npm data](data/popularity-npm-raw.json) and [source limits](POPULARITY-SOURCES.md).

| Complete calendar weeks with both data sources | Weeks | Possible bug reports | npm requests | Reports per million requests |
| --- | ---: | ---: | ---: | ---: |
| Before merge | 25 | 1,678 | 22,569,677 | 74.35 |
| After merge | 24 | 2,378 | 70,795,178 | 33.59 |
| After stable release, included above | 10 | 1,373 | 35,842,116 | 38.31 |

Each period rate is total reports divided by total npm requests. It is not the mean of the weekly rates. Partial weeks and dates without both sources are excluded. Weeks start on Thursday at 00:00 UTC. The merge and stable release occurred later on their boundary days, so these weeks can include hours on both sides of an event. The issue window starts on 13 November at 08:09:34 UTC. Its first week is partial. The final week starts on 29 October and is also partial. npm data ends on 28 October.

Reports cover all installation methods and versions. npm covers one installation method. Changes in automated builds or installation methods can change the rate without changing defect risk. We do not add platform-package downloads to `bun` downloads because one installation can request both.

GitHub stars show interest. The saved current total is 96,468. The final star-history week is partial, and its day boundaries may differ from UTC. Stars are not used to calculate report rates. Current GitHub release-download counters are shown separately because they do not provide past daily counts.

## Daily chart by reported version

The first chart stacks report types for each UTC report-opening day. Choose all versions, one version, or the four most-reported single versions. Choose problem types or named components. Each report enters one stack group: its single match, “Several type matches”, or “No title match”. The stack height equals the number of reports. The separate component comparison permits several matches per report.

`versions.py` first checks the Bun version field in the report template. It then checks explicit text next to the word Bun. Bare library versions are not accepted. Base versions must appear in the saved official release list. Unknown new canary bases can therefore be missed. Rejected candidates remain in the audit data. Reports with several versions form a separate group. Missing versions are unknown. Canary, debug, and dev suffixes remain; individual build IDs are grouped. A plain `1.4.0` does not identify stable or canary. A stated version does not confirm an affected runtime.

[data/versions.jsonl](data/versions.jsonl) stores candidates, evidence, and stack groups. [data/version-daily.json](data/version-daily.json) stores daily totals. `verify_versions.py` checks version rules and confirms that each report enters each chart once.

## Growth and rates

The default chart shows a growth index. Each series uses its own before-merge daily mean as 100. In the four-version view, report bars share the combined reference for the selected versions. Their contributions add to the selected report index. npm uses its own reference. A version with no before-merge reports has no report growth index. Use Counts to view it.

The seven-day option uses complete calendar windows. Counts show daily means. Rates divide the window's total reports by its total npm requests. The report summary uses all included dates. Zoom and hidden series do not change that summary. Version filters still use npm requests across all versions.

The complete-day comparison has **181 days before** the merge (14 November–13 May) and **167 days after** it (15 May–28 October). It excludes the merge day, partial report days, and missing npm dates. Reports per day rise **9.79 → 14.12 (1.44×)**. npm requests per day rise **127,502 → 422,401 (3.31×)**. The period rate falls **76.78 → 33.43 per million requests (−56.5%)**. Reports grew more slowly than npm requests. This does not measure defect risk or active users. The weekly table uses different date limits, so its rates differ slightly.

The [crash and memory comparison](SAFETY-2026-10-30.md) checks explicit leaks separately from other memory problems. It also shows the body text check. A separate chart divides the report growth index by the npm growth index. Its reference is 1. All charts use the same complete-day rules.

## Build and verify

- `pnpm run rebuild`: build from saved data, without network access.
- `pnpm run refresh`: collect issues, npm counts, and star history, then build. This does not update the separately dated GitHub repository and asset snapshot.
- `python3 part3/popularity.py`: build download and star data from saved responses.
- `pnpm run verify`: check counts, dates, version rules, leak rules, and chart calculations.
- From `scripts/`, run `python3 09-verify.py` to check the original report.

`classify.py` defines title rules. `safety.py` defines explicit leak rules. `build.py` builds the report. `block.html` contains the current page and charts. `combined-series.js` supplies the same calculations to the browser and README figures. Its tests check missing dates, zero request counts, partial days, time windows, and growth references. The built HTML includes its data and chart libraries for offline use.
