# -*- coding: utf-8 -*-
"""Haly: fetch a user's contribution calendar and weave it into a carpet.

    python haly.py --user octocat --out dist/carpet.svg        # needs GITHUB_TOKEN
    python haly.py --input calendar.json --out carpet.svg      # offline
    python haly.py --user octocat --style yomut --inscription '{user} {year}'

Uses only the standard library plus fonttools.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import carpet

QUERY = '''query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''


def fetch(login, token, api='https://api.github.com/graphql'):
    body = json.dumps({'query': QUERY, 'variables': {'login': login}}).encode()
    req = urllib.request.Request(api, data=body, headers={
        'Authorization': 'bearer ' + token,
        'Content-Type': 'application/json',
        'User-Agent': 'haly-action',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit('GitHub API returned %d: %s' % (e.code, e.read().decode(errors='replace')[:300]))
    if data.get('errors'):
        sys.exit('GitHub API: ' + '; '.join(e.get('message', '?') for e in data['errors']))
    if not (data.get('data') or {}).get('user'):
        sys.exit('No GitHub user called %r.' % login)
    return data


def main(argv=None):
    p = argparse.ArgumentParser(description='Weave a GitHub contribution year into a Turkmen carpet.')
    p.add_argument('--user', help='GitHub login to weave')
    p.add_argument('--input', help='read a saved GraphQL response instead of calling the API')
    p.add_argument('--out', default='dist/carpet.svg', help='where to write the SVG')
    p.add_argument('--no-animation', action='store_true', help='skip the weaving animation')
    p.add_argument('--style', default='tekke',
                   help='weaving group: tekke, yomut, salor, saryk or ersari')
    p.add_argument('--inscription', default='',
                   help='text knotted into the top border; {user}, {year}, {total} are filled in')
    p.add_argument('--api', default=os.environ.get('GITHUB_GRAPHQL_URL', 'https://api.github.com/graphql'))
    a = p.parse_args(argv)

    if a.input:
        with open(a.input, encoding='utf-8') as f:
            data = json.load(f)
    else:
        if not a.user:
            p.error('give --user, or --input for offline use')
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not token:
            sys.exit('Set GITHUB_TOKEN (any token works; read:user adds private contributions).')
        data = fetch(a.user, token, a.api)

    cal = data['data']['user']['contributionsCollection']['contributionCalendar']
    if not cal['weeks']:
        sys.exit('The contribution calendar came back empty.')

    svg = carpet.build(data, animate=not a.no_animation, style=a.style,
                       inscription=a.inscription, user=a.user or '')
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg)
    print('woven %s contributions -> %s (%d KB)'
          % (format(cal['totalContributions'], ','), a.out, len(svg.encode()) // 1024))


if __name__ == '__main__':
    main()
