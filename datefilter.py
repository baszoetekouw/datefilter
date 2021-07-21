#!/usr/bin/env python3

# this script takes a nuber of datetimes as input and a selection filter, and returns the dates which should be removed
# form the list to comply to the selection filter

import sys
import re
from datetime import datetime, timedelta
from typing import Optional
from pprint import pprint

DEBUG = True
NOW = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

filters_t = list[dict[str, timedelta]]
FILTERS: filters_t = [
    {"period": timedelta(days= 14), "frequency": timedelta(hours=1)},  # keep hourly for 2 weeks
    {"period": timedelta(days= 28), "frequency": timedelta(days= 1)},  # after that, keep daily for 4 weeks
    {"period": timedelta(days= 90), "frequency": timedelta(days= 7)},  # after that, keep weekly for 90 days
    {"period": timedelta(days=365), "frequency": timedelta(days=14)},  # after that, keep biweekly for a year
]


def debug(*args, **kwargs) -> None:
    if DEBUG:
        print(*args, **kwargs)


def pdebug(*args, **kwargs) -> None:
    if DEBUG:
        pprint(*args, **kwargs)


# extract an iso8601-like part of a string and return the corresponding date
def date_from_string(s: str) -> Optional[datetime]:
    # regexp to extract date from strings
    iso8601_regex = r'[0-9]{4}-?[01]\d-?[0123]\d[_T][012]\d:?[0-5]\d(?::?[0-]5\d)?'
    date_re = re.compile(iso8601_regex)

    m = date_re.search(s)
    if not m:
        debug(f"No date found in '{s}'")
        return None
    the_date = datetime.fromisoformat(m[0])
    return the_date


# read a list of string from stdin and extract dates from each
# returns a dict of datetime: original_string
def read_dates() -> dict[datetime, str]:
    str_date: dict[datetime, str] = {}

    # read dates from stdin
    for line in sys.stdin:
        s = line.rstrip()
        the_date = date_from_string(s)

        # make sure dats are unique
        while the_date in str_date:
            the_date += timedelta(milliseconds=1)

        str_date[the_date] = s

    return str_date


# find the filter frequency corresponding to the given age
def find_frequency(filters: filters_t, age: timedelta) -> Optional[timedelta]:
    for filt in sorted(filters, key=lambda p: p['period']):
        if filt['period'] > age:
            return filt['frequency']
    return None


def filter_dates(filters: filters_t, dates: list[datetime]) -> set[datetime]:
    to_keep: set[datetime] = set()
    last_kept = datetime(year=1970, month=1, day=1)

    for d in sorted(dates):
        debug(f'Considering date={str(d)}')
        age = NOW - d
        freq = find_frequency(filters, age)
        debug(f'  since last kept: {str(d-last_kept)}')
        debug(f'  freq is {freq}')
        if freq and d-last_kept > freq:
            debug(f'  keeping')
            to_keep.add(d)
            last_kept = d
        else:
            debug(f'  discarding')

    return to_keep


def main():
    str_date = read_dates()

    dates = sorted(list(str_date.keys()), reverse=True)

    to_keep = filter_dates(FILTERS, dates)
    to_remove = set(dates) - to_keep

    if DEBUG:
        print("=====================")
        for d in dates:
            print(f'{str_date[d]} {d}: {"keeping" if d in to_keep else "REMOVE"}')
        print("=====================")

    for s in sorted(to_remove):
        print(s)


if __name__ == "__main__":
    main()
