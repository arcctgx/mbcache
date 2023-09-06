"""Fetch release data from MusicBrainz based on MBID."""

import argparse
import musicbrainzngs
from mbcache import ReleaseCache, APPNAME, VERSION, URL


def parse_args():
    parser = argparse.ArgumentParser(
        description='Fetch release data from MusicBrainz based on MBID')
    parser.add_argument('mbid', help='release MBID to fetch data for')
    parser.add_argument('-d',
                        '--disambiguation',
                        default=None,
                        help='disambiguation string (only used for storing)')
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def get_from_musicbrainz(album_mbid):
    musicbrainzngs.set_useragent(APPNAME, VERSION, URL)

    try:
        result = musicbrainzngs.get_release_by_id(
            album_mbid, includes=['artists', 'recordings', 'artist-credits'])
    except musicbrainzngs.ResponseError as exc:
        print(f'Failed to look up release MBID {album_mbid}: {exc}')
        return None

    try:
        release = result['release']
        return release
    except KeyError:
        print(f'Query for MBID {album_mbid} returned empty result!')
        return None


def get_from_cache(cache, mbid, disambiguation=None):
    data = cache.lookup_id(mbid)
    if data is None:
        data = get_from_musicbrainz(mbid)
        if data is not None:
            cache.store(data['artist-credit-phrase'], data['title'], data, disambiguation)

    return data


def main():
    args = parse_args()
    cache = ReleaseCache()
    release_data = get_from_cache(cache, args.mbid, args.disambiguation)

    if release_data is not None:
        print(release_data)


if __name__ == '__main__':
    main()
