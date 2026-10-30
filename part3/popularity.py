#!/usr/bin/env python3
"""Collect public usage proxies, or rebuild their combined payload offline.

    python3 part3/popularity.py --fetch
    python3 part3/popularity.py               # committed cache only

GitHub's connected fetch tool does not allow the documented star-history path;
the public REST endpoint is the fallback. No auth token or user list is needed.
"""
import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent / 'data'
START = dt.date(2025, 11, 13)
UTC = dt.timezone.utc


def get(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'bun-rust-rewrite-analysis',
        'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'application/json',
    })
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def save(name, payload):
    (DATA / name).write_text(json.dumps(payload, indent=2) + '\n')


def fetch():
    now = dt.datetime.now(UTC)
    # The range endpoint can return zero for days not processed yet. Ask for
    # the latest *available* day before deciding where to stop the series.
    last_day = get('https://api.npmjs.org/downloads/point/last-day/bun')
    available = dt.date.fromisoformat(last_day['end'])
    end = min(now.date() - dt.timedelta(days=1), available)
    url = f'https://api.npmjs.org/downloads/range/{START}:{end}/bun'
    npm = get(url)
    assert npm['package'] == 'bun'
    assert npm['start'] == START.isoformat() and npm['end'] == end.isoformat()
    expected = {(START + dt.timedelta(days=i)).isoformat() for i in range((end - START).days + 1)}
    assert {r['day'] for r in npm['downloads']} == expected
    assert len(npm['downloads']) == len(expected)
    assert all(isinstance(r['downloads'], int) and r['downloads'] >= 0 for r in npm['downloads'])
    assert next(r['downloads'] for r in npm['downloads'] if r['day'] == last_day['end']) == last_day['downloads']
    save('popularity-npm-raw.json', {'generated': now.isoformat(timespec='seconds'),
        'source': url, 'last_day_probe': last_day, 'response': npm})

    stars = []
    urls = []
    for page in range(1, 101):
        url = f'https://api.github.com/repos/oven-sh/bun/stargazers/history?per_page=30&page={page}'
        result = get(url)
        assert isinstance(result, list)
        stars.extend(result)
        urls.append(url)
        if not result or min(r['week'] for r in result) <= dt.datetime.combine(START, dt.time(), UTC).timestamp():
            break
    else:
        raise RuntimeError('Star-history pagination limit reached before baseline')
    assert len(stars) == len({r['week'] for r in stars})
    assert all(len(r['days']) == 7 and sum(r['days']) == r['total'] for r in stars)
    save('popularity-stars-raw.json', {'generated': now.isoformat(timespec='seconds'),
        'sources': urls, 'weeks': stars})


def rebuild():
    npm = json.loads((DATA / 'popularity-npm-raw.json').read_text())
    stars = json.loads((DATA / 'popularity-stars-raw.json').read_text())
    github = json.loads((DATA / 'popularity-github-snapshot.json').read_text())
    observed = dt.datetime.fromisoformat(stars['generated'])
    # The weekly epoch is rendered in UTC for a common x axis. GitHub says
    # star-history boundaries are not guaranteed to align with UTC, so do not
    # pretend this is a precise daily exposure series.
    weekly = []
    for row in sorted(stars['weeks'], key=lambda r: r['week']):
        start = dt.datetime.fromtimestamp(row['week'], UTC)
        if start.date() + dt.timedelta(days=7) <= START:
            continue
        weekly.append({**row, 'day': start.date().isoformat(),
            'complete': start + dt.timedelta(days=7) <= observed})
    payload = {
        'generated': max(npm['generated'], stars['generated'], github['generated']),
        'npm': {'package': 'bun', 'source': npm['source'],
            'generated': npm['generated'], 'requested_start': npm['response']['start'],
            'requested_end': npm['response']['end'], 'valid_through': npm['response']['end'],
            'daily': npm['response']['downloads'], 'last_day_probe': npm['last_day_probe']},
        'github': {'snapshot': {**github['snapshot'], 'generated': github['generated']},
            'stars_sources': stars['sources'], 'stars_generated': stars['generated'],
            'stars_weekly': weekly, 'release_assets': github['release_assets']},
        'limits': [
            'npm tarball requests include automation and mirrors; they do not count unique or active users.',
            'npm covers one installation channel, excluding direct script, Homebrew, Scoop and Docker installs.',
            'Do not add bun and its platform packages: one install can request both.',
            'npm historical range counts aggregate versions; the long series cannot split Zig/Rust or stable/canary.',
            'GitHub release download_count is a cumulative asset counter observed now, not downloads by historical day.',
            'Release asset sums may include upgrades, automation, profile builds and more than one download per person.',
            'Stars measure interest; weekly star boundaries need not be UTC and are not an exposure denominator.',
            'Do not add npm counts to GitHub asset counters; channels can overlap through installers and fallback paths.',
        ],
    }
    save('popularity.json', payload)
    print(f"npm: {len(payload['npm']['daily'])} complete daily observations through {payload['npm']['valid_through']}")
    print(f"stars: {len(weekly)} weekly bins, latest complete={weekly[-1]['complete']}")
    print(f"current snapshot: {github['snapshot']['stars']:,} stars; {len(github['release_assets'])} releases with cumulative asset counters")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='refresh npm and aggregate star history from public APIs')
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        fetch()
    rebuild()
