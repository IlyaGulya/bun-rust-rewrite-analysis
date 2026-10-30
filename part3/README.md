# Report dates, stated versions, and inferred families

The [current HTML](../index.html) and [main README](../README.md) separate three questions:

1. When was the report opened: before merge, during the Rust canary period, or after Rust stable?
2. Which Bun version does the saved text state?
3. Which version family can be inferred from that text?

These measures do not establish the cause of a defect or actual runtime exposure.

## Date periods

Full report groups use exact timestamps: merge **14 May 2026, 08:09:34 UTC** and stable **20 August 2026, 14:07:21 UTC**. Their possible-bug totals are **1,802 / 1,004 / 1,385**. Stable remained Zig during the canary period. Reports after stable can concern old versions.

Rate tables require complete paired UTC days. They exclude both event days, the first/last partial issue days, and missing npm dates. The three periods have **181 / 97 / 69 days** and **1,772 / 985 / 1,338 possible bug reports**. The corresponding npm totals are **23,077,916 / 34,698,894 / 35,306,720**. [Safety calculations](SAFETY-2026-10-30.md) define these groups.

## Text rules

`classify.py` applies the same title rules in every period. Component and problem matches can overlap. A missing match does not prove absence of a problem. Labels only supply the inherited possible-bug exclusion rule. Unlabelled feature requests can pass it.

The body text check adds up to 2,500 characters after removing fenced code and template prompts. It can include unrelated mentions. [Saved matches](data/classified.jsonl) retain evidence. Before-merge text and labels were observed in August; later data in October. The [36-report review](CLASSIFICATION-AUDIT.md) found wrong and missed matches. It does not estimate overall accuracy.

## Version extraction and family inference

`versions.py` prefers the report template's Bun version field. It then checks explicitly adjacent Bun-version strings. Bare dependency versions are not accepted. Base versions must appear in saved official release history. New unrecognised canary bases can be missed. Rejected candidates remain in the audit. Suffixes are preserved; individual build IDs are grouped.

One usable version appears in **2,918** reports. **857** have no usable version and **416** have several versions. The family rule assigns **1,910 Zig-line**, **980 Rust-line**, and **1,301 unclear** reports:

- Base versions below 1.4 are Zig-line. Old canary/dev/debug strings after merge remain unclear.
- Base versions from 1.4 are Rust-line only after the exact merge timestamp. Earlier mentions have conflicting dates and stay unclear.
- Missing or multiple versions stay unclear. They are never assigned by report date.

A plain `1.4.0` cannot identify stable or canary. These are version-line inferences, not binary checks. Edits after filing can create impossible-looking version dates. Per-report records keep the inference reason in [versions.jsonl](data/versions.jsonl).

## Version-family map

[family-matrix.json](data/family-matrix.json) stores weekly direct title-match counts for every family/version row. Weeks start Thursday at 00:00 UTC. Weeks can cross event timestamps. The first and last issue weeks are partial. All **4,191** reports remain represented.

The interactive map filters family and problem type. Its default shows the 12 most-reported clear versions, remaining-version groups, and unclear groups. The every-version view exposes all rows. Colour uses fixed count ranges shared across rows. No row has its own intensity scale. Zero is distinct from a missing download observation.

Selecting a cell chooses the stated version, one-day counts, and that week in the daily chart. The native version selector provides keyboard access to the same detail. The npm context line shows daily means for complete weeks across all versions. It does not normalize individual version rows. [Design and reading guide](INFOGRAPHIC.md).

The daily stack counts each report once: its single problem match, several matches, or no match. The map uses direct matches, so a crash can count even if its title also matches another type. Its leak option uses the separate explicit-memory rule.

## Counts, growth, and rates

The daily chart defaults to counts. Growth divides each series by its own before-merge daily mean and multiplies by 100. Family and version filters change only report counts. npm requests remain across all versions. A version with no before-merge reference has no report growth index; counts remain available.

Seven-day windows use complete calendar windows. Counts show daily means. Rates divide the window's total reports by total requests. The three summary periods are disjoint and exclude both event days. Zoom does not change summaries. The separate Q chart divides the current report/request rate by its before-merge reference.

June-to-October npm daily means rose **348,054 → 533,390**, about **1.53×**. This differs from a comparison of long periods before/after merge. None of these request ratios counts active users. The [source file](POPULARITY-SOURCES.md) records dates and limits.

## Reproduction

- `pnpm run rebuild`: build from committed inputs, without network.
- `pnpm run refresh`: collect issues, npm counts, and stars, then build. Separately dated repository/asset counters are not refreshed by this command.
- `pnpm run verify`: check counts, boundaries, daily stacks, matrix conservation, family ambiguity, and rates.
- `python3 part3/popularity.py`: build popularity data from saved responses.
- From `scripts/`, run `python3 09-verify.py` for the original August report.

`combined-series.js` supplies shared calculations to the browser and README figures. Python safety exports are checked independently against it. The built current HTML includes the data and chart libraries for offline use. [Original August report](../archive/report-2026-08-10.html).
