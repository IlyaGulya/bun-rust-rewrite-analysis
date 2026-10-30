# Bun's Rust rewrite: bug reports, release delivery and download growth

An updated fork of [Aleksandr Smyshliaev's original study](https://github.com/asmyshlyaev177/bun-rust-rewrite-analysis) of [oven-sh/bun#30412](https://github.com/oven-sh/bun/pull/30412). The report now follows issue arrivals through **30 October 2026**, with daily version/type stacks, npm downloads, GitHub interest, and separate crash and memory-leak comparisons.

**[Open the interactive report](https://bun-rust-analysis-ilyagulya.netlify.app/)**

[Combined chart](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-version-daily) · [Crashes and leaks](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-safety) · [Reports / audience-proxy growth](https://bun-rust-analysis-ilyagulya.netlify.app/#p3-growth-ratio) · [Original August analysis](archive/README-2026-08-10.md)

The HTML is self-contained: [download `index.html`](https://raw.githubusercontent.com/IlyaGulya/bun-rust-rewrite-analysis/master/index.html) and open it locally. The published Netlify site serves this same file. The original August charts remain in the report's collapsed historical appendix.

## Current snapshot

| Item | Observation |
| --- | --- |
| Rewrite merged | **14 May 2026, 08:09:34 UTC** |
| First Rust stable | **1.4.0, 20 August 2026** — 98 calendar days after the merge |
| Latest observed stable | **1.4.4, 22 October 2026** |
| Issue pull | **30 October 2026, 09:20:14 UTC**; current day is partial |
| npm downloads | Daily observations through **28 October 2026**; unpublished days are gaps |
| Comparison corpus | **1,802 pre-merge + 2,389 post-merge potential defect reports** |
| Post-merge issue cohort | 2,568 issues; 1,022 still open at the pull |
| Pre-merge source | Frozen August snapshot; post-merge labels and outcomes are refreshed |

“Potential defect reports” retains the original label-exclusion definition; it can include untriaged non-bugs. These are reports, not independently confirmed or deduplicated defects.

## Findings on comparable full days

The normalization uses **181 pre-merge days** (14 November–13 May) and **167 post-merge days** (15 May–28 October). It excludes the merge day, partial issue-window endpoints and unpublished download dates. npm denominators are **23,077,916** and **70,541,010** requests.

| Primary title signal | Before: reports | Before: per million npm requests | After: reports | After: per million npm requests | Rate change |
| --- | ---: | ---: | ---: | ---: | ---: |
| All potential defect reports | 1,772 | 76.78 | 2,358 | 33.43 | **−56.5%** |
| Crash / fatal signal | 404 | 17.51 | 190 | 2.69 | **−84.6%** |
| Explicit memory leak / retained allocations | 15 | 0.65 | 13 | 0.18 | **−71.6%** |

Average report arrivals rose **1.44×**, while average npm requests rose **3.31×**. Report growth was slower than this distribution-activity proxy over the matched periods. The separate relative-growth chart divides the report-growth index by the npm-download index; its pooled post/pre comparison is **0.435×**, with **1** as the pre-merge report/download reference.

The crash/leak direction survives a sensitivity pass that adds the first 2,500 body characters: crash-signal rates change **24.74 → 4.34**, explicit leak/retention rates **1.26 → 0.24** per million npm requests. That sensitivity pass can pick up incidental mentions and formatting differences; it is not classifier validation.

**The narrow conclusion is about report indicators, not a causal Rust benefit.** There are only **15 → 13** primary leak reports, so much of the normalized decline comes from growth in the download denominator. npm counts package requests, including CI/repeats, rather than active users; it misses other installation channels and cannot provide a historical per-version denominator here. Arrival-time cohorts include multiple builds, and a post-merge report can concern an older Zig build. Title specificity, triage, issue mix and exposure also changed.

Stable delivery resumed: the August statement that nothing had shipped is now historical. Likewise, canary-only version heuristics from part 1 cannot be applied after 1.4.0 became stable. [Post-stable analysis](part2/UPDATE-2026-10-30.md) and [primary release sources](part2/SOURCES-2026-10-30.md) document the timeline.

## What the interactive report contains

- **One combined daily chart:** exclusive type stacks, a version filter or grouped version stacks, and an npm-download line. Switch between counts, a common growth index (`pre = 100`), reports per million downloads, and composition. Choose daily or trailing seven-day values.
- **Separate crash/leak rates:** before/after counts and rates, title-only/body sensitivity, 1/7/28-day windows, and inspectable links to the memory-retention reports. Generic OOM/high memory use remains a separate category.
- **Report growth / npm growth:** a separate ratio chart. Below 1 means fewer reports per npm request than the pre-period reference; a rising curve means reports are outpacing requests over that interval, even if still below 1.
- **Provisional classification:** components and symptoms, coverage/unclassified shares, body sensitivity, and searchable issue-title evidence. The daily stacks count every report once; multiple signals and unknowns are explicit buckets.
- **Follow-up and context:** age-restricted 30-day closure shares, releases, weekly star arrivals and dated cumulative binary-asset counters. Stars measure interest; current asset totals cannot reconstruct historical daily downloads.

The primary taxonomy is rule-based title matching. It is exploratory, multi-label in the comparison table, and exclusive only in the daily stacks. The [36-report spot check](part3/CLASSIFICATION-AUDIT.md) found false positives and omissions; no overall accuracy or recall estimate is claimed. Version parsing prefers the Bun version field or explicit Bun version strings, checks saved release bases, and preserves ambiguous/unknown reports. It does not confirm which runtime caused a bug.

## Reproduce and verify

Requirements: **Python 3**, **Node.js** and **pnpm**. No network is needed after installing the pinned chart dependencies.

```bash
pnpm install --frozen-lockfile
pnpm run rebuild       # rebuild from committed snapshots; no API requests
pnpm run verify        # cohort, classification, exposure, version and safety checks
pnpm run site          # package the already-built HTML into dist/ for static hosting
```

`pnpm run refresh` collects a **new observation** of issues, npm downloads and star history, then rebuilds. It requires network access and can change past counts as reports are relabelled or closed. Repository/release-asset counter snapshots have their own observation timestamps; that command does not refresh those counters. The ignored full-body cache is optional for an offline rebuild: committed slim records and bounded excerpts provide the inputs.

The original August-only verification remains separate:

```bash
(cd scripts && python3 09-verify.py)  # 31 checks for the frozen original analysis
```

## Sources and files

| Path | Purpose |
| --- | --- |
| [`index.html`](index.html) | Complete offline-capable interactive report |
| [`archive/README-2026-08-10.md`](archive/README-2026-08-10.md) | Preserved original analysis and its historical conclusions |
| [`data/`](data/) and [`scripts/`](scripts/) | Frozen part 1 evidence and verification |
| [`part2/`](part2/README.md) | Refreshed post-merge issues, stable releases and closure follow-up |
| [`part3/README.md`](part3/README.md) | Taxonomy, version stacks and adoption comparison |
| [`part3/SAFETY-2026-10-30.md`](part3/SAFETY-2026-10-30.md) | Crash/leak definitions, rates, sensitivity and relative-growth formula |
| [`part3/POPULARITY-SOURCES.md`](part3/POPULARITY-SOURCES.md) | Primary npm/GitHub sources and exposure limitations |
| [`part3/data/`](part3/data/) | Saved source responses, classified records, version/type counts and safety audit |
| [`scripts/package-site.py`](scripts/package-site.py) | Packages the prebuilt report without fetching or recomputing data |

The older complete-week comparison and newer complete-day comparison use different inclusion boundaries; their slightly different rates should not be mixed. Every derived table records its denominators and observation window.

## Publication and attribution

This fork's current report is published at **[bun-rust-analysis-ilyagulya.netlify.app](https://bun-rust-analysis-ilyagulya.netlify.app/)**. Netlify serves a manually deployed, versioned static artifact; GitHub is the source of record. A future GitHub push does not automatically publish a new Netlify deploy.

To update the linked Netlify project after rebuilding and verifying:

```bash
pnpm run site
pnpm --package=netlify-cli@24.0.1 dlx netlify deploy --site bun-rust-analysis-ilyagulya --prod --no-build --dir=dist
```

The pinned, isolated CLI avoids conflicts with globally installed packages and uses your existing Netlify login.

`.netlify/`, `dist/`, scratch work and the full raw issue cache are ignored. Only the rendered report and license are packaged for web publication.

The original study and its historical discussion are by **Aleksandr Smyshliaev**. This fork extends that work with the October snapshot, classifications, adoption proxies and additional charts. Code/report licensing remains [MIT](LICENSE); copyright in quoted issue text belongs to its authors. See [CITATION.cff](CITATION.cff) for the updated fork citation.
