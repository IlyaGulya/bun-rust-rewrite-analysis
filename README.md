# Bun after the Rust rewrite

Bun merged [PR #30412](https://github.com/oven-sh/bun/pull/30412) on 14 May 2026. The change replaced its Zig runtime with Rust. This report extends [Aleksandr Smyshliaev's original study](https://github.com/asmyshlyaev177/bun-rust-rewrite-analysis) through **30 October 2026**.

![Report types and npm requests on one growth scale. Each series uses its own before-merge daily mean as 100. npm requests grow faster after the merge.](assets/readme/01-growth-and-reports.png)

**[Open the interactive report](https://bun-rust-analysis-ilyagulya.netlify.app/)** · [Crashes and memory leaks](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-safety) · [Reports compared with downloads](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-growth-ratio)

The six charts below work directly on GitHub. Use the HTML report to zoom and select versions. You can also [download the HTML](https://raw.githubusercontent.com/IlyaGulya/bun-rust-rewrite-analysis/master/index.html) and open it offline.

## Main results

**Report counts grew more slowly than npm requests.** Reports per day increased **1.44 times**. npm requests per day increased **3.31 times**. Reports per million npm requests decreased **56.5%**.

**Crash and memory-leak report rates also decreased.** The crash rate decreased **84.6%**. The memory-leak rate decreased **71.6%**. There were only **15 memory-leak reports before and 13 after**.

**Stable releases resumed.** Bun released 1.4.0 on 20 August. Four patches followed. The latest stable version in this data is 1.4.4, released on 22 October.

These results describe reports and download activity. **They do not show that Rust caused fewer defects.** npm requests include repeat downloads and automated jobs. They do not count active users.

## Read the numbers correctly

| Term | Meaning |
| --- | --- |
| **Possible bug report** | A GitHub issue that passes the label filter. Some reports may describe features or duplicate defects. |
| **npm request** | A download request for package `bun`. One person or job can make many requests. |
| **Title match** | A word pattern in an issue title. It does not prove the cause of a defect. |
| **Period rate** | Total reports divided by total npm requests for the same complete days. |
| **Growth index** | Daily mean divided by its before-merge mean, then multiplied by 100. |
| **Relative report rate** | Report growth index divided by npm growth index. The reference is 1. |

The report uses fixed data snapshots. The matching rules, source files and limits are linked below.

| Data or event | Value |
| --- | --- |
| Rewrite merged | **14 May 2026, 08:09:34 UTC** |
| Change size | +1,009,257 / −4,024 lines; 2,188 files; 6,755 commits |
| Report window | 13 November 2025 → **30 October 2026** |
| Possible bug reports | **1,802 before + 2,389 after = 4,191** |
| Issue data collected | 30 October, 09:20 UTC. That day is incomplete. |
| npm data available | Through **28 October** |
| First Rust stable release | **1.4.0, 20 August**. This was 98 calendar days after the merge. |
| Latest stable in the snapshot | **1.4.4, 22 October** |
| Original report | [August source text](archive/README-2026-08-10.md) |

## Reports and download activity

The first chart uses a common growth scale. Each series has its own before-merge mean of 100. The colours show report types. The white line shows npm requests. Each daily point uses the previous seven days.

| Complete-day comparison | Before merge | After merge | Change |
| --- | ---: | ---: | ---: |
| Days | 181 | 167 | The periods have different lengths. |
| Possible bug reports | 1,772 | 2,358 | Compare rates, not counts alone. |
| Reports per day | 9.79 | 14.12 | **1.44×** |
| npm requests | 23,077,916 | 70,541,010 | This covers one download channel. |
| npm requests per day | 127,502 | 422,401 | **3.31×** |
| Reports per million requests | 76.78 | 33.43 | **−56.5%** |

The periods are **14 November–13 May** and **15 May–28 October**. We exclude the merge day and incomplete days. We also exclude days without published npm data. This explains why these report counts are smaller than the full 1,802/2,389 groups.

Existing users can file reports without a new download. Automated jobs can download Bun many times. Direct installers, embedded Bun and Docker may not appear in the npm count. These differences can change the ratio without a change in product quality.

## Crashes and memory leaks

![Separate before-and-after rate charts for crashes and memory leaks. Each chart shows reports per million npm requests and the raw report count.](assets/readme/02-crashes-and-leaks.png)

| Title match | Before: count | Before: per million | After: count | After: per million | Rate change |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crash or fatal signal | 404 | 17.51 | 190 | 2.69 | **−84.6%** |
| Memory leak or memory not released | 15 | 0.65 | 13 | 0.18 | **−71.6%** |
| All memory problems, as a separate check | 27 | 1.17 | 25 | 0.35 | **−69.7%** |

The leak rule requires evidence that allocated memory was not released. It includes native memory, garbage-collector roots and request-body bytes. It also includes leaks found when a process exits.

High memory use or an out-of-memory error alone does not meet this rule. Leaked disk files and file descriptors do not meet it either. These reports remain in the full input and can match other rules.

**Most of the leak-rate decrease comes from download growth.** The report counts, 15 before and 13 after, are close. The number of npm requests is much larger after the merge.

The HTML report links all **28 leak reports** in this comparison. [Inspect the evidence](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-safety).

We also repeat the calculation with up to 2,500 body characters added to each title:

| Extra body-text check | Before: count | Before: per million | After: count | After: per million | Rate change |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crash or fatal signal | 571 | 24.74 | 306 | 4.34 | −82.5% |
| Memory leak or memory not released | 29 | 1.26 | 17 | 0.24 | −80.8% |

The rates still decrease. This does not validate the matching rules. Body text can mention a problem that did not occur. Old and new excerpts also have different text formats.

The crash rule has known false matches, such as text about crash-report metadata. Reports may also describe the same defect. [Read the definitions and calculations](part3/SAFETY-2026-10-30.md).

## Do reports grow faster than downloads?

![Report growth divided by npm growth. The reference line is 1. Values below 1 mean fewer reports per npm request than before the merge.](assets/readme/03-relative-growth.png)

The chart calculates:

```text
Q = report growth index / npm growth index
  = current report/request rate / before-merge period rate
```

- **Q = 1:** the report/request rate equals the before-merge reference.
- **Q < 1:** the rate is lower than that reference.
- **Q > 1:** the rate is higher than that reference.
- **Q is rising:** reports grow faster than npm requests over that interval. Q can rise while it remains below 1.

The full-period after/before ratio is **0.435×**. Each moving-window value divides the sum of reports by the sum of requests. It does not average the daily ratios. The full-period value is not the average of the moving-window curve.

[Open the chart](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-growth-ratio) to select all reports, crashes or memory problems. You can use windows of 1, 7 or 28 days.

## Report types

![Before-and-after shares of component names in issue titles. HTTP and test mentions increase. Package-installation mentions decrease. Many titles have no component match.](assets/readme/04-component-mix.png)

| Component named in the title | Before: 1,802 reports | After: 2,389 reports |
| --- | ---: | ---: |
| HTTP and networks | 162 (8.99%) | 353 (14.78%) |
| Tests | 37 (2.05%) | 176 (7.37%) |
| Package installation | 152 (8.44%) | 135 (5.65%) |
| Build and code conversion | 112 (6.22%) | 157 (6.57%) |
| SQL and storage | 67 (3.72%) | 105 (4.40%) |
| **No component match** | **1,110 (61.60%)** | **1,154 (48.30%)** |

These counts describe words in titles. They do not confirm which component failed. A report can name several components. Titles also became more specific after the merge.

The comparison table permits several matches per report. The daily stacks use one group per report. One match keeps its type. Several matches use the **several types** group. No match uses the **no type match** group.

We checked [36 reports with at least one match](part3/CLASSIFICATION-AUDIT.md). We found incorrect matches and missing matches. This sample does not measure the accuracy of all classifications.

## Reported versions by day

![Daily report-type stacks for Bun 1.3.14, 1.4.0 and 1.4.4. The three panels use the same dates and count scale.](assets/readme/05-daily-versions.png)

These panels show **three selected versions**, not all Bun reports. [Use the HTML chart](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-version-daily) to select other versions or all reports.

| Version information in 4,191 reports | Count |
| --- | ---: |
| One usable version | 2,918 |
| No usable version | 857 |
| Several versions | 416 |

The parser first reads the Bun version field. It then checks explicit Bun-version text if needed. It checks the base version against saved releases. This helps reject editor, extension and operating-system versions entered in the wrong field.

The parser keeps `canary` and `debug` suffixes. It groups build hashes. Unknown and unreleased base versions remain unknown.

A plain **`1.4.0` does not identify the release channel**. A version in a report does not prove which build caused the problem. Later edits can also change the version text. We have no historical npm denominator for each version. [Read the version evidence](part3/data/versions.jsonl).

## Releases and fixes

![Weekly reports split into marked-as-fixed and other outcomes. The release strip shows the first Rust stable after 98 days and four later patches.](assets/readme/06-release-and-followup.png)

Bun released **1.4.0 on 20 August**. This was 98 calendar days after the rewrite merge. Four stable patches followed:

| Version | Release date in 2026 |
| --- | --- |
| 1.4.1 | 4 September |
| 1.4.2 | 5 September |
| 1.4.3 | 10 October |
| 1.4.4 | 22 October |

The August report said that no Rust build had reached stable. That statement applies to its original date. [Read the release-source check](part2/SOURCES-2026-10-30.md).

Recent reports have less time to get a fix. The next table includes only reports that are at least 30 days old:

| Report group | Reports old enough | Marked as fixed within 30 days | Share |
| --- | ---: | ---: | ---: |
| Before merge | 1,802 | 478 | **26.5%** |
| Merge to first Rust stable | 1,004 | 297 | **29.6%** |
| After stable 1.4.0 | 796 | 192 | **24.1%** |
| All after-merge reports | 1,800 | 489 | **27.2%** |

The overall after-merge share is close to the before-merge share. The after-stable share is lower.

“Marked as fixed” means GitHub records the issue as `closed` with reason `completed`. It does not prove a fix shipped. A reopened report counts as unresolved. We cannot recover every earlier close and reopen event.

Before-merge states remain fixed at the August snapshot. After-merge states were updated in October. [Read the fixes analysis](part2/UPDATE-2026-10-30.md).

## Limits

The data shows that stable releases resumed. It also shows lower report-per-request rates. It does not separate a Rust effect from other changes.

- **Downloads do not count users.** npm covers one channel. It includes automated and repeat requests.
- **Opening dates do not identify the runtime.** After-merge reports can concern older Zig builds.
- **Reports do not count unique defects.** Several reports can describe one defect. The label filter can admit feature requests.
- **Text rules can be wrong.** Titles differ in detail. Memory-safety causes require case review.
- **The snapshots have different dates.** Before-merge text, labels and states come from August. After-merge observations come from October.
- **The periods differ.** Daily and weekly comparisons exclude different boundary dates. Do not mix their rates.

The [original August report](archive/README-2026-08-10.md) also discusses Rust complexity and AI-assisted development. Its source quotations remain unchanged.

## Rebuild the report

Use Python 3, Node.js and pnpm. After you install the dependencies, these commands use saved data:

```bash
pnpm install --frozen-lockfile
pnpm run rebuild
pnpm run verify
pnpm run site
```

Use Python 3.12 or later to render the README figures:

```bash
python3 -m venv .venv-readme
.venv-readme/bin/pip install -r requirements-readme.txt
.venv-readme/bin/python scripts/render-readme-charts.py
```

<details>
<summary>Source files and publishing commands</summary>

| Path | Purpose |
| --- | --- |
| [`index.html`](index.html) | Current HTML report |
| [`assets/readme/`](assets/readme/) | Six figures and their data manifest |
| [`scripts/render-readme-charts.py`](scripts/render-readme-charts.py) | Figure renderer |
| [`archive/README-2026-08-10.md`](archive/README-2026-08-10.md) | Original source text |
| [`archive/report-2026-08-10.html`](archive/report-2026-08-10.html) | Original HTML report |
| [`data/`](data/) and [`scripts/`](scripts/) | Original data and checks |
| [`part2/`](part2/README.md) | Releases and issue states |
| [`part3/README.md`](part3/README.md) | Type rules, versions and download comparisons |
| [`part3/SAFETY-2026-10-30.md`](part3/SAFETY-2026-10-30.md) | Crash and memory calculations |
| [`part3/POPULARITY-SOURCES.md`](part3/POPULARITY-SOURCES.md) | npm and GitHub sources |
| [`part3/data/`](part3/data/) | Saved inputs and per-issue evidence |
| [`WRITING.md`](WRITING.md) | Writing rules and term definitions |

`pnpm run refresh` collects new issue, npm and star data. It can change old counts when reports change. Update the README and figures after a refresh. Release-asset counters have separate observation dates.

Run the original checks from their script directory:

```bash
(cd scripts && python3 09-verify.py)
```

A GitHub push does not publish a new Netlify site version. After you rebuild and verify the report, run:

```bash
pnpm run site
pnpm --package=netlify-cli@24.0.1 dlx netlify deploy --site bun-rust-analysis-ilyagulya --prod --no-build --dir=dist
```

Local settings, output folders and scratch work are ignored. The web package contains the current report, the original report and the license.

</details>

## Credits and license

**Aleksandr Smyshliaev** wrote the original study. This fork adds the October data, type rules, download comparisons and charts.

The code and report use the [MIT license](LICENSE). Issue authors retain copyright in their text. [CITATION.cff](CITATION.cff) gives the fork citation. The current web report is at **[bun-rust-analysis-ilyagulya.netlify.app](https://bun-rust-analysis-ilyagulya.netlify.app/)**.
