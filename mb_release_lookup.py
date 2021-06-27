#!/usr/bin/env python3

import argparse
import musicbrainzngs
from cache import ReleaseCache

def parse_args():
    parser = argparse.ArgumentParser(description='Fetch release data from MusicBrainz based on MBID')
    parser.add_argument('mbid', help='release MBID to fetch data for')

    return parser.parse_args()


def get_from_musicbrainz(album_mbid):
    musicbrainzngs.set_useragent('mbcache', 'v0.1.0a')

    try:
        result = musicbrainzngs.get_release_by_id(album_mbid, includes=['artists', 'recordings', 'artist-credits'])
    except musicbrainzngs.ResponseError as e:
        print('Failed to look up release MBID %s: %s' % (album_mbid, str(e)))
        return None

    try:
        release = result['release']
        return release
    except KeyError:
        print('Query for MBID %s returned empty result!' % album_mbid)
        return None


def get_from_cache(cache, mbid):
    data = cache.lookup_id(mbid)
    if data is None:
        data = get_from_musicbrainz(mbid)
        if data is not None:
            cache.store(data['artist-credit-phrase'], data['title'], data)

    return data


def main():
    args = parse_args()
    cache = ReleaseCache()
    release_data = get_from_cache(cache, args.mbid)

    if release_data is not None:
        print(release_data)


if __name__ == '__main__':
    main()
