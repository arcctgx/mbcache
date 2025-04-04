"""Copy recordings from a release to the recordings cache."""

import argparse
import sys
from typing import Dict, List, Optional, Tuple

from mbnames import remove_featured

from mbcache import MbRecordingCache, MbReleaseCache
from mbcache.params import _RecordingParams
from mbcache.version import VERSION


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Copy recordings from a release to the recordings cache.')

    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='release title')

    parser.add_argument('-d',
                        '--disambiguation',
                        default=None,
                        help='release disambiguation string')

    parser.add_argument('-n',
                        '--dry-run',
                        action='store_true',
                        help='do not copy, just show what would be added to cache')

    parser.add_argument('-F',
                        '--feat-string',
                        default=None,
                        help='truncate the artist credit starting from this string')

    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def _make_tracklist(release: Dict,
                    feat_string: Optional[str]) -> List[Tuple[str, _RecordingParams]]:
    tracklist = []
    album = release['title']

    for medium in release['medium-list']:
        tracks = medium['track-list']
        if 'pregap' in medium:
            # include pregap track if it exists in the medium.
            tracks = [medium['pregap']] + medium['track-list']

        for track in tracks:
            # skip video tracks
            if track['recording'].get('video', False):
                continue

            # prefer track title over recording title
            try:
                title = track['title']
            except KeyError:
                title = track['recording']['title']

            artist = track['artist-credit-phrase']
            if len(track['artist-credit']) == 1:
                # use canonical names on non-compound artists by default
                artist = track['artist-credit'][0]['artist']['name']

            artist = remove_featured(artist, feat_string)

            mbid = track['recording']['id']
            params = _RecordingParams(artist, title, album)
            tracklist.append((mbid, params))

    return tracklist


# pylint: disable=protected-access
def _convert_release(release: Dict, args) -> None:
    cache = MbRecordingCache()
    added = 0

    for track in _make_tracklist(release, args.feat_string):
        mbid, params = track

        if cache._cache.exists(params):
            print(f'Recording {mbid} is already in the cache.')
            continue

        if args.dry_run:
            print('Would add: ', params.key())
            continue

        cache._cache.store(mbid, params)
        added += 1

    if added > 0:
        print(f'Added {added} recordings to the cache.')


def main():
    args = _parse_args()
    releases = MbReleaseCache()
    release = releases.get(args.artist, args.title, args.disambiguation)

    if release is None:
        sys.exit('Failed to get the release!')

    _convert_release(release, args)


if __name__ == '__main__':
    main()
