"""Find MusicBrainz recording based on artist, title and album."""

import argparse

from mbcache import MbRecordingCache
from mbcache.version import VERSION


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Find MusicBrainz recording based on artist, title and album.')

    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='recording title')
    parser.add_argument('album', help='album title')

    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def main():
    args = _parse_args()
    cache = MbRecordingCache()
    mbid = cache.get(args.artist, args.title, args.album)

    if mbid is not None:
        print(mbid)


if __name__ == '__main__':
    main()
