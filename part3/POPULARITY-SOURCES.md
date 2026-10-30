# Bun downloads and GitHub stars — 30 October 2026

[Saved data](data/popularity.json) contains 350 daily npm counts, 51 weeks of GitHub star history, and a dated GitHub repository and release-asset snapshot. Run [popularity.py](popularity.py) to build from saved responses. Add `--fetch` to collect npm and star data again. The [GitHub snapshot](data/popularity-github-snapshot.json) was collected separately through the connected GitHub tool.

## npm requests for `bun`

The npm API counts package downloads by day. Date limits include both endpoints. npm processes logs after UTC midnight. `last-day` means the latest processed day, which can be earlier than yesterday. Total download history is available for up to 18 months. Version-specific history covers only the previous seven days. Our long series therefore cannot separate versions, Zig from Rust, or stable from canary. [API documentation](https://github.com/npm/registry/blob/main/docs/download-counts.md).

The latest-day check returned **969,715 requests on 28 October 2026**. A range request through 29 October returned zero for that day, while the latest-day check still ended on the 28th. We exclude the unprocessed day. The saved series covers **13 November 2025 to 28 October 2026**. [Latest-day endpoint](https://api.npmjs.org/downloads/point/last-day/bun), [dated endpoint](https://api.npmjs.org/downloads/range/2025-11-13:2026-10-28/bun), [saved response](data/popularity-npm-raw.json).

| Calendar month | npm downloads | Days covered | Mean/day |
| --- | ---: | ---: | ---: |
| April 2026 | 5,149,448 | 30 | 171,648 |
| May 2026 | 7,306,881 | 31 | 235,706 |
| June 2026 | 10,441,614 | 30 | 348,054 |
| July 2026 | 12,316,670 | 31 | 397,312 |
| August 2026 | 13,401,303 | 31 | 432,300 |
| September 2026 | 15,213,584 | 30 | 507,119 |
| October 1–28 | 14,934,927 | 28 | 533,390 |


Totals sum the saved daily counts. Only the daily mean is rounded. May includes dates before and after the merge. August includes dates before and after stable 1.4.0. These calendar months do not isolate either event.

npm counts served package archives. Automated builds, mirrors, and robots can add counts. Cached downloads can avoid a new count. npm recommends using the trend rather than treating the count as users. Our reports-per-million rate compares reports from all installation methods with requests from one method. It is not a failure probability or defects per active user. [npm counting method](https://blog.npmjs.org/post/92574016600/numeric-precision-matters-how-npm-download-counts-work.html).

The `bun` package installs the runtime and lists platform binaries as optional dependencies. One installation can request both packages. Do not add their counts. [Package metadata](https://registry.npmjs.org/bun/latest). Bun also supports installation scripts, Homebrew, Scoop, Docker, and direct downloads. Existing installations can upgrade through other methods. [Installation documentation](https://bun.com/docs/installation).

## GitHub stars

GitHub provides weekly star history with a total and seven daily counts. We collected two pages and kept weeks that overlap the study dates. The week starting **25 October is partial**. GitHub does not guarantee UTC day boundaries. The chart uses UTC date labels but does not use stars to calculate report rates. [API documentation](https://docs.github.com/en/rest/activity/starring#get-repository-star-history), [API page 1](https://api.github.com/repos/oven-sh/bun/stargazers/history?per_page=30&page=1), [saved history](data/popularity-stars-raw.json).

The connected GitHub tool did not allow this endpoint. The collector used the public API instead. It did not collect individual user lists.

The dated snapshot has **96,468 stars**, **5,234 forks**, and **612 subscribers**. Stars show interest, not runtime use. Current totals cannot show the past installed base. GitHub distinguishes stars from subscribers, and current star counts exclude removed stars. [Repository API](https://api.github.com/repos/oven-sh/bun), [starring documentation](https://docs.github.com/en/rest/activity/starring), [saved snapshot](data/popularity-github-snapshot.json).

## GitHub release-download counters

Release assets have a cumulative `download_count`. The API does not give historical daily downloads. One current reading cannot split counts into the periods before and after the merge. Future daily changes would require repeated dated readings. [Release-asset API](https://docs.github.com/en/rest/releases/assets#get-a-release-asset).

The saved data covers 17 stable releases published since the study began. On 30 October, totals for all listed assets were **24,756,510 for 1.3.14**, **5,075,252 for 1.4.0**, and **2,049,312 for 1.4.4**. The saved file also keeps individual counters and a ZIP-only total. Releases have different ages. The totals include several platforms and build variants. They cannot serve as comparable period rates. [Releases API](https://api.github.com/repos/oven-sh/bun/releases?per_page=100&page=1), [saved assets](data/popularity-github-snapshot.json).

We do not add npm and GitHub counts. Users, upgrades, and installer fallback requests can overlap. Other installation methods are absent. The report uses daily npm counts and shows stars separately. Actual defect risk would require active-use counts by build and information about how often users report problems. These snapshots do not provide either.

## Growth depends on the chosen dates

June has **10,441,614 requests over 30 days**, or **348,054/day**. October 1–28 has **14,934,927 over 28 days**, or **533,390/day**. The daily-mean ratio is **1.53×**. A ratio using all dates before and after merge answers a different question. Neither is a user-growth estimate.

The report now uses separate before-merge, canary-period, and after-stable summaries. npm still covers all versions in every period. We do not divide Zig-line or Rust-line reports by an assumed share of npm requests.
