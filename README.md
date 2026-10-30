# One PR, a million lines of Rust — what happened next?

On 14 May 2026, Bun merged [PR #30412](https://github.com/oven-sh/bun/pull/30412): a million-line Zig-to-Rust rewrite. This follow-up extends [Aleksandr Smyshliaev's original study](https://github.com/asmyshlyaev177/bun-rust-rewrite-analysis) through **30 October 2026**, comparing report patterns, release delivery and npm distribution activity.

![Daily problem-type stacks and npm downloads indexed to their own pre-merge means of 100. The npm line rises faster than the report stack after the rewrite. Trailing seven-day series extend through October; missing download dates remain gaps.](assets/readme/01-growth-and-reports.png)

**[Explore the interactive report →](https://bun-rust-analysis-ilyagulya.netlify.app/)** · [Crashes and leaks](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-safety) · [Reports versus audience growth](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-growth-ratio)

All figures below render directly on GitHub. The HTML adds zoom, version filters, title/body sensitivity and inspectable issue evidence; it also [works offline](https://raw.githubusercontent.com/IlyaGulya/bun-rust-rewrite-analysis/master/index.html).

| Study context | Observation |
| --- | --- |
| **Rewrite** | [PR #30412](https://github.com/oven-sh/bun/pull/30412), merged **14 May 2026, 08:09:34 UTC** |
| **Scale** | +1,009,257 / −4,024 lines; 2,188 files; 6,755 commits |
| **Report window** | 13 November 2025 → **30 October 2026** |
| **Potential defect reports** | **1,802 before + 2,389 after = 4,191** |
| **Issue observation** | 30 October, 09:20 UTC; that calendar day is partial |
| **npm observation** | Daily `bun` package requests through **28 October** |
| **First Rust stable** | **1.4.0, 20 August** — 98 calendar days after the merge |
| **Latest observed stable** | **1.4.4, 22 October** |
| **Historical reference** | [Original August analysis](archive/README-2026-08-10.md), preserved separately |

## What the new data says

**Reports increased, but npm requests increased faster.** On complete, matched calendar days, report arrivals rose **1.44×**, while npm requests rose **3.31×**. The all-report ratio fell from **76.78 to 33.43 reports per million npm requests**.

**Crash and memory-retention report indicators also fell.** The title-based crash rate declined **84.6%**; the explicit memory-leak/retention rate declined **71.6%**. The leak numerator itself barely changed: **15 reports before, 13 after**.

**The shipping interruption ended.** The original August conclusion that no Rust build had reached stable is now historical. Stable 1.4.0 arrived on 20 August; four patches followed through 22 October.

These are observations about **report indicators and distribution activity**. npm requests include CI and repeats, omit other installation channels and do not count active users. The data cannot establish that Rust caused a change in defect risk.

## More reports, much more download activity

The hero chart places both series on a common scale: each is divided by its own pre-merge daily mean and multiplied by 100. The stacked bars preserve the problem-type mix; the white line shows npm-request growth. A trailing seven-day mean reduces daily noise.

| Matched full-day comparison | Before merge | After merge | Change |
| --- | ---: | ---: | ---: |
| Days observed | 181 | 167 | Different window lengths |
| Potential reports | 1,772 | 2,358 | Counts need an exposure comparison |
| Reports / day | 9.79 | 14.12 | **1.44×** |
| npm requests | 23,077,916 | 70,541,010 | One distribution channel |
| npm requests / day | 127,502 | 422,401 | **3.31×** |
| Reports / million npm requests | 76.78 | 33.43 | **−56.5%** |

The matched periods are **14 November–13 May** and **15 May–28 October**. We exclude the merge day, the partial first/last issue-window days, and unpublished downloads. These smaller numerators therefore differ from the full 1,802/2,389 cohorts above.

This is an exposure *proxy*, not a measured installed base. Existing users can report without downloading Bun again; one CI job can download it repeatedly; direct installers, embedded Bun, Docker and other channels need not contribute to the npm denominator. A shift in that channel mix can change the ratio without changing quality.

## Crashes and memory retention per million requests

![Two before/after comparisons with separate scales: crash report rates fall from 17.51 to 2.69 per million npm requests; explicit memory-leak or retention report rates fall from 0.65 to 0.18. Labels retain the raw sample sizes.](assets/readme/02-crashes-and-leaks.png)

| Primary title signal | Before: reports | Before: / million | After: reports | After: / million | Rate change |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crash / fatal signal | 404 | 17.51 | 190 | 2.69 | **−84.6%** |
| Explicit memory leak / retained allocations | 15 | 0.65 | 13 | 0.18 | **−71.6%** |
| Broad memory / OOM / corruption, separate check | 27 | 1.17 | 25 | 0.35 | **−69.7%** |

The narrow leak signal requires explicit allocation-retention evidence: leaked native memory, GC roots, request-body bytes or similar retained allocations. Generic OOM/high memory use remains a separate class. Disk/temp-file growth, file-descriptor leaks and a memory-cap test flake are excluded. Leaks detected at process shutdown are included.

**For leaks, the denominator does most of the work.** Fifteen reports over 181 days and thirteen over 167 days are similar daily arrival rates. The strong per-million decline chiefly reflects growing npm traffic. The [28 matched primary leak-signal reports](part3/data/safety-audit.jsonl) remain auditable; the [interactive evidence table](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-safety) links each one.

A sensitivity pass adds at most 2,500 body characters on both sides:

| Bounded-body sensitivity | Before: reports | Before: / million | After: reports | After: / million | Rate change |
| --- | ---: | ---: | ---: | ---: | ---: |
| Crash / fatal signal | 571 | 24.74 | 306 | 4.34 | −82.5% |
| Explicit memory leak / retention | 29 | 1.26 | 17 | 0.24 | −80.8% |

The direction survives that variant. It is not classifier validation: body mentions can be incidental or negated, and the old plain-text and newer Markdown excerpts differ in formatting. The legacy crash rule also has known false positives such as crash-report metadata. Counts concern reports, not independently confirmed or deduplicated failures. [Definitions, evidence and calculations](part3/SAFETY-2026-10-30.md).

## Are bugs outgrowing the audience proxy?

![The ratio of report growth to npm-request growth over time. The horizontal reference is 1. Seven-day and twenty-eight-day windows are shown, and the pooled post/pre comparison is 0.435.](assets/readme/03-relative-growth.png)

The separate graph answers the growth question directly:

```text
Q = report-growth index / npm-download-growth index
  = current reports-per-request rate / pooled pre-merge reports-per-request rate
```

- **Q = 1:** the report/request ratio equals the pre-period reference.
- **Q < 1:** fewer reports per npm request than that reference.
- **Q > 1:** more reports per npm request than that reference.
- **A rising Q:** reports are outpacing the npm proxy over that interval, even if Q remains below 1.

The all-report pooled post/pre result is **0.435×**. This divides rate levels against a fixed baseline; it does not divide potentially zero or negative percentage-growth numbers. Rolling values use **ratios of sums** within complete windows. The pooled result is not the unweighted average of the rolling curve.

[Open this chart](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-growth-ratio) to switch between all reports, crashes, explicit memory retention and broad memory signals, or between 1/7/28-day windows.

## What kinds of reports changed?

![Before/after shares of component mentions in issue titles. HTTP/network and test-runner mentions rise; package-manager mentions fall. The chart excludes the large no-component-signal group from the bars and reports its coverage in the footnote.](assets/readme/04-component-mix.png)

| Component title signal | Before: 1,802 reports | After: 2,389 reports |
| --- | ---: | ---: |
| HTTP / network | 162 (8.99%) | 353 (14.78%) |
| Test runner | 37 (2.05%) | 176 (7.37%) |
| Package manager | 152 (8.44%) | 135 (5.65%) |
| Bundler / transpiler | 112 (6.22%) | 157 (6.57%) |
| SQL / storage | 67 (3.72%) | 105 (4.40%) |
| **No component title signal** | **1,110 (61.60%)** | **1,154 (48.30%)** |

These are **provisional title mentions**, not validated affected subsystems or root causes. Categories overlap. Titles became more specific across the two snapshots, and many reports name no component. Thus the component-share changes cannot by themselves establish that networking worsened or package installation improved.

Components and symptoms are separate axes. The comparison table uses multi-label counts; the daily stacks use exclusive buckets: one matching signal keeps its class, several become **multiple signals**, none become **no title signal**. Every report enters a stack exactly once. A [36-report conditional spot check](part3/CLASSIFICATION-AUDIT.md) found false positives and omissions; it does not estimate overall accuracy or recall.

## Reported Bun versions, day by day

![Daily problem-type stacks for three selected reported versions: Bun 1.3.14, 1.4.0 and 1.4.4. All three panels share date and count scales. Unknown and multiple signals remain in the stack.](assets/readme/05-daily-versions.png)

The panels show three selected versions on the same calendar-day and count scales. **They are not all-version totals.** The [interactive version](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-version-daily) includes every extracted version, an all-version aggregate, grouped version comparisons and npm overlays.

| Version extraction over all 4,191 potential reports | Reports |
| --- | ---: |
| A single usable reported version | 2,918 |
| Unknown / unusable version | 857 |
| Multiple reported versions | 416 |

The extractor prefers the issue template's Bun version field, then explicit adjacent Bun-version strings. Base versions are checked against saved official release history because reporters sometimes put editor, extension or kernel versions in the Bun field. Canary/debug suffixes are retained while build hashes are grouped. Unrecognised or unreleased bases remain unknown.

A **plain `1.4.0` does not identify stable versus canary**. A reported version does not prove which runtime caused a bug, and later edits can change version text. Counts have no historical per-version npm denominator, so a more frequently reported version is not necessarily less reliable. [Version evidence](part3/data/versions.jsonl).

## Stable shipping resumed; follow-up is a different question

![Whole-window weekly potential reports split into closed-as-fixed and other outcomes, with stable-release dates below. The release strip highlights 98 days from the rewrite merge to the first Rust stable, followed by four patch releases. Edge weeks are partial.](assets/readme/06-release-and-followup.png)

Bun **1.4.0 shipped on 20 August**, 98 calendar days after the merge. It was followed by **1.4.1 (4 September)**, **1.4.2 (5 September)**, **1.4.3 (10 October)** and **1.4.4 (22 October)**. The release-drought statements in the [August analysis](archive/README-2026-08-10.md) describe that historical window, not the current state. [Primary release-source verification](part2/SOURCES-2026-10-30.md).

Closure shares need equal follow-up. The age-restricted comparison includes only potential bug reports at least 30 days old:

| Arrival cohort | Eligible reports | Closed as fixed within 30 days | Share |
| --- | ---: | ---: | ---: |
| Before merge, frozen baseline | 1,802 | 478 | **26.5%** |
| Merge → first Rust stable, all builds | 1,004 | 297 | **29.6%** |
| Since stable 1.4.0, all builds | 796 | 192 | **24.1%** |
| All post-merge | 1,800 | 489 | **27.2%** |

The overall post-merge share is close to the frozen baseline; the post-stable subset is lower. GitHub's current `closed`/`completed` state is a maintainer disposition, not proof that a verified fix shipped. Reopened reports count as unresolved. Medians among fixed reports omit unresolved cases, and reconstructed backlog lacks intermediate reopen/reclose events. The baseline's states remain frozen in August while post-merge states were refreshed in October. [Full follow-up analysis](part2/UPDATE-2026-10-30.md).

## What this study can and cannot establish

The data supports three descriptive conclusions: **stable delivery resumed**, **npm distribution activity grew faster than report arrivals**, and **crash/leak report-per-request indicators fell**. It does not isolate a programming-language effect.

The limits that matter to those conclusions are:

- **Exposure is unmeasured.** npm traffic is one installation-channel proxy, including CI and repeats. GitHub stars measure interest, not runtime use; current cumulative binary-asset counters cannot reconstruct historical daily downloads.
- **Arrival time is not implementation.** Post-merge reports include old Zig builds; canary availability, stable adoption and reporting incentives changed.
- **Reports are not unique confirmed defects.** One defect can produce several issues. The inherited label-exclusion definition can admit untriaged feature requests; triage coverage changed.
- **Classification is exploratory.** Title specificity and excerpt formats differ. Root causes, severity and memory-safety guarantees require case-level investigation.
- **Snapshots have different observation dates.** Baseline text/labels/outcomes were observed in August; post-merge ones in October. A frozen historical comparison is not a randomized control.
- **Calendar boundaries matter.** The main normalization excludes partial days and the merge day. Older complete-week tables use different inclusion windows and therefore slightly different rates. Windows crossing the merge contain both periods.

The original report also discusses Rust's complexity, AI-assisted porting and verification. Those contextual arguments and their quotations remain available in the [preserved original analysis](archive/README-2026-08-10.md); the October evidence does not settle those broader debates.

## Data and reproduction

The snapshot is committed, and the figures above are generated from it. No API requests are needed for an offline rebuild after installing the pinned chart dependencies.

```bash
pnpm install --frozen-lockfile
pnpm run rebuild       # regenerate the self-contained HTML from saved inputs
pnpm run verify        # classifications, cohorts, exposure joins, versions and safety
pnpm run site          # package the verified HTML for static hosting
```

The rendered README figures use the same rolling/index calculations as the HTML. To regenerate them with Python 3.12+, Node.js and a local plotting environment:

```bash
python3 -m venv .venv-readme
.venv-readme/bin/pip install -r requirements-readme.txt
.venv-readme/bin/python scripts/render-readme-charts.py
```

<details>
<summary>Source files, snapshot refresh and publication</summary>

| Path | Purpose |
| --- | --- |
| [`index.html`](index.html) | Complete offline-capable interactive report |
| [`assets/readme/`](assets/readme/) | The six rendered GitHub figures and their snapshot manifest |
| [`scripts/render-readme-charts.py`](scripts/render-readme-charts.py) | Reproducible static-figure renderer |
| [`archive/README-2026-08-10.md`](archive/README-2026-08-10.md) | Original analysis and historical conclusions |
| [`data/`](data/) and [`scripts/`](scripts/) | Frozen part 1 evidence and verification |
| [`part2/`](part2/README.md) | Post-merge issues, releases and follow-up |
| [`part3/README.md`](part3/README.md) | Classification, version stacks and adoption methods |
| [`part3/SAFETY-2026-10-30.md`](part3/SAFETY-2026-10-30.md) | Crash/leak definitions, rates, sensitivity and relative-growth formula |
| [`part3/POPULARITY-SOURCES.md`](part3/POPULARITY-SOURCES.md) | Primary npm/GitHub sources and denominator limits |
| [`part3/data/`](part3/data/) | Saved source responses, classified evidence and audit records |

`pnpm run refresh` collects a **new observation** of issues, npm downloads and star history, then rebuilds the HTML. It can change historical counts as reports are edited, relabelled or closed. Refresh the static figures and README claims too when changing the snapshot. Repository/release-asset counters have separate timestamps and are not refreshed by that command. The full-body cache is optional for an offline rebuild; committed slim records and bounded excerpts supply the inputs.

The original verification remains separate:

```bash
(cd scripts && python3 09-verify.py)  # 31 checks on frozen part 1
```

Netlify serves a manually published static artifact. A GitHub push does not automatically redeploy it. To update the site after rebuilding and verifying:

```bash
pnpm run site
pnpm --package=netlify-cli@24.0.1 dlx netlify deploy --site bun-rust-analysis-ilyagulya --prod --no-build --dir=dist
```

`.netlify/`, `dist/`, local plotting environments, scratch work and the full raw issue cache are ignored. Only rendered HTML and the license are packaged for web publication.

</details>

## Attribution and license

The original study is by **Aleksandr Smyshliaev**. This fork extends it with the October snapshot, version/type classification, adoption proxies and additional charts. The original text and its historical context are preserved in the archive.

Code/report licensing remains [MIT](LICENSE); copyright in quoted issue text belongs to its authors. [CITATION.cff](CITATION.cff) records the updated fork citation. The current web report is published at **[bun-rust-analysis-ilyagulya.netlify.app](https://bun-rust-analysis-ilyagulya.netlify.app/)**.
