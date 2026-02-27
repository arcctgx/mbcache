"""Find MusicBrainz release based on artist and title."""

import argparse
import json

from mbcache import MbReleaseCache
from mbcache.version import VERSION


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Find MusicBrainz release based on artist and title')

    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='release title')

    parser.add_argument('-d',
                        '--disambiguation',
                        default=None,
                        help='string to distinguish two otherwise identically named releases')

    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def main():
    args = _parse_args()
    cache = MbReleaseCache()
    release = cache.get(args.artist, args.title, args.disambiguation)

    if release is not None:
        print(json.dumps(release, indent=1))


if __name__ == '__main__':
    main()
