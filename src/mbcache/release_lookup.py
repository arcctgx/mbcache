"""Find MusicBrainz release based on MBID."""

import argparse
import json

from mbcache import MbReleaseCache
from mbcache.version import VERSION


def _parse_args():
    parser = argparse.ArgumentParser(description='Find MusicBrainz release based on MBID')

    parser.add_argument('mbid', help='release MBID to fetch data for')

    parser.add_argument('-d',
                        '--disambiguation',
                        default=None,
                        help='disambiguation string (only used for storing)')

    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def main():
    args = _parse_args()
    cache = MbReleaseCache()
    release = cache.get_mbid(args.mbid, args.disambiguation)

    if release is not None:
        print(json.dumps(release, indent=1))


if __name__ == '__main__':
    main()
