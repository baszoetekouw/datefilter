#!/usr/bin/env python3

# this script takes a number of string containing iso8601-like dates as input and a selection filter,
# and returns the dates which should be removed from the list to comply to the selection filter

import sys
import re
import argparse
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List, Set, Union

DEBUG = False
ORS = "\n"  # output record separator

#NOW = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
NOW = datetime.now()

try:
    filters_t = List[Dict[str, timedelta]]
except TypeError:
    filters_t = Any

FILTERS: filters_t = [
    {"period": timedelta(days= 14), "frequency": timedelta(hours=1)},  # keep hourly for 2 weeks  # noqa: E251
    {"period": timedelta(days= 28), "frequency": timedelta(days= 1)},  # keep daily for 4 weeks   # noqa: E251
    {"period": timedelta(days= 90), "frequency": timedelta(days= 7)},  # keep weekly for 90 days  # noqa: E251
    {"period": timedelta(days=365), "frequency": timedelta(days=14)},  # keep biweekly for a year # noqa: E251
]


def debug(*args, **kwargs) -> None:
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


def td_format(td_object: timedelta) -> str:
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('week',        60*60*24*7),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings: List[str] = []
    seconds = int(td_object.total_seconds())
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value > 1:
                plural = 's'
                period_value = str(period_value) + " "
            else:
                plural = ''
                period_value = ''
            strings.append(f"{period_value}{period_name}{plural}")

    return ", ".join(strings)


def show_filter(filters: filters_t) -> None:
    print("Current filter rules:")
    for filt in filters:
        p = filt['period']
        f = filt['frequency']

        print(f' - keep a file every {td_format(f)} for the past {td_format(p)}')

    sys.exit(0)


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
def read_dates() -> Dict[datetime, str]:
    str_date: Dict[datetime, str] = {}

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


def filter_dates(filters: filters_t, dates: List[datetime]) -> Set[datetime]:
    to_keep: Set[datetime] = set()
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


def handle_args() -> Dict[str, Union[str, int]]:
    global DEBUG

    parser = argparse.ArgumentParser(
        description="""
            Read a list of strings from stdin, extracts a date out of each one and returns
            the ones to discard according to a filter spec
        """
    )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="show debugging info")
    parser.add_argument('-0', '--print0',
                        action='store_true',
                        help="use \\0 as output separator (for piping to 'xargs -0')")
    parser.add_argument('-f', '--force',
                        action='store_true',
                        help="force output even if we would output (almost) everything")
    parser.add_argument('-s', '--show-filter',
                        action='store_true',
                        dest='show_filter',
                        help="the the current filter rules")
    parser.add_argument('-m', '--min-keep',
                        action='store',
                        type=int,
                        default=10,
                        dest='min_keep',
                        help="minimum number of file to keep (default: 10)")
    options = parser.parse_args()

    if options.debug:
        DEBUG = True

    if options.show_filter:
        show_filter(FILTERS)

    return {
        "ors": "\0" if options.print0 else "\n",
        "force": options.force,
        "min_keep": options.min_keep
    }


def main() -> None:
    options = handle_args()

    str_date = read_dates()
    dates = sorted(list(str_date.keys()), reverse=True)

    to_keep = filter_dates(FILTERS, dates)
    to_remove = set(dates) - to_keep

    if DEBUG:
        print("=====================")
        for d in dates:
            print(f'{str_date[d]} {d}: {"keeping" if d in to_keep else "REMOVE"}')
        print("=====================")

    num_to_keep   = len(to_keep)  # noqa: E221
    num_to_remove = len(to_remove)
    if not options['force'] and num_to_remove > 0 and num_to_keep < num_to_remove and num_to_keep < options['min_keep']:
        print(f"Would remove {num_to_remove} files and keep only {num_to_keep}; respectfully refusing.",
              file=sys.stderr)
        print(f"Override with --force if this is really what you want", file=sys.stderr)
        return

    for s in sorted(to_remove):
        print(str_date[s], end=options['ors'])


if __name__ == "__main__":
    main()
