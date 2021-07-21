#!/usr/bin/env python3

# this script takes a nuber of datetimes as input and a selection filter, and returns the dates which should be removed
# form the list to comply to the selection filter

import sys
import re
from datetime import datetime, timedelta
from pprint import pprint

DEBUG = True
NOW = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

filters: list[dict[int]] = [
    {"period":   5 * 24 * 60 * 60, "frequency":           60 * 60},  # keep hourly for 5 days
    {"period":  14 * 24 * 60 * 60, "frequency":      24 * 60 * 60},  # after that, keep daily for two weeks
    {"period":  30 * 24 * 60 * 60, "frequency":  7 * 24 * 60 * 60},  # after that, keep weekly for 90 days
    {"period": 365 * 24 * 60 * 60, "frequency": 14 * 24 * 60 * 60},  # after that, keep biweekly for a year
]


# itereare over time; starting at now, counting backwards with steps of freq for a period of period
def age_range(period: timedelta, frequency: timedelta):
    age = timedelta(0)
    while age < period:
        yield age
        age += frequency


def debug(*args, **kwargs) -> None:
    if DEBUG:
        print(*args, **kwargs)


def pdebug(*args, **kwargs) -> None:
    if DEBUG:
        pprint(*args, **kwargs)


# read dates from stdin
dates: list[datetime] = []
date_re = re.compile('[0-9][0-9_:-]+')
for line in sys.stdin:
    this_date = datetime.fromisoformat(line.rstrip())
    dates.append(this_date)

dates.sort(reverse=True)
pdebug(dates)

to_keep: set[datetime] = set()
try:
    date_iter = iter(dates)
    the_date = next(date_iter)
    age = timedelta(0)
    for current_filter in sorted(filters, key=lambda d: d['period']):
        period    = timedelta(seconds=current_filter['period'])
        frequency = timedelta(seconds=current_filter['frequency'])
        debug(period, frequency)
        while age < period:
            debug(f"  {age}")
            while the_date:
                date_age = NOW - the_date
                debug(f"     considering {age} for date {date_age}")
                if age < date_age:
                    break
                elif age >= date_age and age < date_age + frequency:
                    debug(f" --> found {the_date}")
                    to_keep.add(the_date)
                    the_date = next(date_iter)
                    # continue counting from the matched date
                    age = date_age + frequency
                    break
                else:
                    debug(f" --> discarding {the_date}")
                    the_date = next(date_iter)
            age += frequency
except StopIteration:
    pass


to_remove = set(dates) - to_keep

if DEBUG:
    print("=====================")
    print("Will keep:")
    for s in sorted(to_keep):
        print(f"  - {s}")
    print("Will remove:")
    for s in sorted(to_remove):
        print(f"  - {s}")
    print("=====================")

for s in sorted(to_remove):
    print(s)
