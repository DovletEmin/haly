"""Writes a synthetic contribution calendar, for trying Haly offline."""
import datetime
import json
import math
import random

rng = random.Random(7)
end = datetime.date(2026, 11, 12)
start = end - datetime.timedelta(days=end.weekday() + 1 + 52 * 7)   # a Sunday
weeks, day = [], start
while day <= end:
    week = []
    for _ in range(7):
        if day > end:
            break
        season = 0.55 + 0.45 * math.sin((day - start).days / 58.0)
        busy = rng.random() < season * (0.35 if day.weekday() >= 5 else 0.8)
        week.append({'date': day.isoformat(),
                     'contributionCount': int(rng.expovariate(1 / (6 * season))) + 1 if busy else 0})
        day += datetime.timedelta(days=1)
    weeks.append({'contributionDays': week})

total = sum(d['contributionCount'] for w in weeks for d in w['contributionDays'])
json.dump({'data': {'user': {'contributionsCollection': {
    'totalCommitContributions': total,
    'totalRepositoriesWithContributedCommits': 21,
    'contributionCalendar': {'totalContributions': total, 'weeks': weeks}}}}},
    open('sample.json', 'w'), indent=1)
print('wrote sample.json,', total, 'contributions')
