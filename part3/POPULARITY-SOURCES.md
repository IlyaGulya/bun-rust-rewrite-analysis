# Bun popularity and download proxies — 30 October 2026

The combined, offline-readable payload is [data/popularity.json](data/popularity.json). It contains 350 daily npm observations, 51 GitHub star-history weeks, and a dated GitHub repository/release-asset snapshot. The collector is [popularity.py](popularity.py): run it without arguments to rebuild from committed caches, or with `--fetch` to refresh the npm and star series. GitHub release metadata was collected separately through the connected GitHub plugin and saved in [data/popularity-github-snapshot.json](data/popularity-github-snapshot.json).

## A useful time series: npm downloads of `bun`

The official npm API returns daily package download counts with inclusive date bounds. Its documentation says logs are processed daily after UTC midnight; `last-day` means the latest available day, which may precede yesterday. Historical aggregate ranges are supported for up to 18 months; historical per-version counts are only available for the previous seven days. Therefore our long series cannot distinguish Zig/Rust, stable/canary or specific Bun versions. [npm API documentation](https://github.com/npm/registry/blob/main/docs/download-counts.md).

The latest-day probe returned **2026-10-28: 969,715 downloads**. A preliminary range query through October 29 returned zero for the 29th while the latest-day probe still stopped on the 28th. That zero was excluded as an unprocessed day, not interpreted as a collapse. The committed series covers **2025-11-13 through 2026-10-28**. [Latest-day endpoint](https://api.npmjs.org/downloads/point/last-day/bun), [dated range endpoint](https://api.npmjs.org/downloads/range/2025-11-13:2026-10-28/bun), [saved response](data/popularity-npm-raw.json).

| Calendar month | npm downloads | Days covered | Mean/day |
| --- | ---: | ---: | ---: |
| April 2026 | 5,149,448 | 30 | 171,648 |
| May 2026 | 7,306,881 | 31 | 235,706 |
| June 2026 | 10,441,614 | 30 | 348,054 |
| July 2026 | 12,316,670 | 31 | 397,312 |
| August 2026 | 13,401,303 | 31 | 432,300 |
| September 2026 | 15,213,584 | 30 | 507,119 |
| October 1–28 | 14,934,927 | 28 | 533,390 |

These values are sums of the committed daily response, rounded only in the mean/day column. May straddles the rewrite and August straddles stable 1.4.0: these calendar rows are descriptive, not clean treatment/control cohorts. [Daily source data](data/popularity-npm-raw.json).

npm defines downloads as served package tarballs; automation, mirrors and robots are included, while cache hits can avoid a new count. npm itself recommends popularity direction rather than user counts. “Reports per million npm downloads” is consequently a ratio of two proxies with different populations; it is not a failure probability or defects per active user. [npm's explanation of its counting method](https://blog.npmjs.org/post/92574016600/numeric-precision-matters-how-npm-download-counts-work.html).

The observed package metadata identifies `bun` as Bun's runtime installer and lists platform binaries as optional dependencies. Do not add downloads of `bun` to all `@oven/bun-*` packages: one installation can request both. [npm package metadata](https://registry.npmjs.org/bun/latest). Bun also documents script, Homebrew, Scoop, Docker and direct-download routes, so npm captures only one distribution channel; existing installations can upgrade independently. [Official installation and upgrade documentation](https://bun.com/docs/installation).

## A separate interest series: GitHub stars

GitHub's current API provides a **weekly aggregate star-history endpoint**, including each week's total and seven daily counts. This avoids collecting personal stargazer lists. The endpoint paginates backward; we collected two pages and retained weeks intersecting the study window. The week beginning **October 25 is incomplete**. GitHub explicitly says week/day boundaries are not guaranteed to align with UTC, so the epoch is rendered as a UTC date label for plotting but must not be treated as precise UTC daily exposure. [Official star-history documentation](https://docs.github.com/en/rest/activity/starring#get-repository-star-history), [API page 1](https://api.github.com/repos/oven-sh/bun/stargazers/history?per_page=30&page=1), [saved aggregate history](data/popularity-stars-raw.json).

The connected GitHub fetch tool rejected this documented endpoint because it is outside that tool's allowed paths; collection therefore used the unauthenticated public REST endpoint. This is recorded in the collector. No individual user list was fetched.

The dated repository snapshot contains **96,468 stars**, **5,234 forks** and **612 watchers/subscribers**. Stars express interest rather than runtime use; current totals are not a historical denominator. Weekly star arrivals are useful as an additional chart about attention, not as an exposure correction. GitHub distinguishes star and subscriber counts, and the current star-count endpoint excludes removed stars; we do not infer a historical cumulative installed base from current totals. [Repository API](https://api.github.com/repos/oven-sh/bun), [GitHub's starring documentation](https://docs.github.com/en/rest/activity/starring), [saved snapshot](data/popularity-github-snapshot.json).

## What GitHub binary counters can and cannot tell us

GitHub release assets expose a cumulative `download_count`, alongside creation/update times; the documented response does not supply downloads by historical day. A single present-day read cannot allocate those downloads to the pre/post windows. To obtain increments prospectively requires separate dated observations. [Official release-asset API schema](https://docs.github.com/en/rest/releases/assets#get-a-release-asset).

The saved metadata contains 17 stable releases published since the baseline began. Illustrative totals across **all listed assets**, observed on October 30, are 24,756,510 for 1.3.14, 5,075,252 for 1.4.0 and 2,049,312 for 1.4.4. The cache also preserves individual asset counters and a separate ZIP-only sum. These are cumulative counts with unequal release ages and include profile/platform variants; they are **not comparable period download rates** and cannot normalize historical issues. [GitHub releases endpoint](https://api.github.com/repos/oven-sh/bun/releases?per_page=100&page=1), [saved assets](data/popularity-github-snapshot.json).

We do not sum npm and GitHub counters: users, upgrades and installer fallback routes can overlap, while downloads through other distribution systems can be absent. The reliable first implementation is an aligned npm volume series plus GitHub star arrivals, with clearly labelled proxy-normalized sensitivity analysis. Measuring actual defect risk would require active-user/build exposure and reporting rates unavailable in these public snapshots.
