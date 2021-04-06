#!/usr/bin/env python3

import argparse
import musicbrainzngs
from cache import ReleaseCache

def parse_args():
    parser = argparse.ArgumentParser( description='Find release MBID based on artist and title.')
    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='release title')

    return parser.parse_args()


def print_search_results(releases):
    count = releases['release-count']

    if count == 0:
        print('Search returned no results!')
    elif count == 1:
        print('Search returned a single result:')
    else:
        print('Search returned %d results:' % count)

    for (idx, release) in enumerate(releases['release-list']):
        score = release['ext:score']
        artist = release['artist-credit-phrase']
        title = release['title']

        try:
            disambiguation = ' (' + release['disambiguation'] + ')'
        except KeyError:
            disambiguation = ''

        # TODO: figure out how to print this nicely
        info = []

        try:
            info.append(release['country'])
        except KeyError:
            pass

        try:
            info.append(release['date'])
        except KeyError:
            pass

        try:
            info.append(release['label-info-list'][0]['label']['name'])
        except KeyError:
            pass

        try:
            info.append(release['label-info-list'][0]['catalog-number'])
        except KeyError:
            pass

        try:
            info.append(release['barcode'])
        except KeyError:
            pass

        print('[%d]\tscore = %s\t%s - "%s" (%s) %s' %
                (idx+1, score, artist, title, ', '.join(info), disambiguation))


def select_from_search_results(releases):
    count = releases['release-count']

    if count == 1:
        return releases['release-list'][0]

    while True:
        index = int(input('Which one to use? (0 - none of these) [0-%d] ' % count))

        if index == 0:
            print('Search result discarded.')
            return None

        if 1 <= index <= count:
            return releases['release-list'][index-1]


def get_from_musicbrainz(artist, title):
    musicbrainzngs.set_useragent('mbcache', 'v0.1.0a')

    releases = musicbrainzngs.search_releases(artist=artist, releaseaccent=title, strict=True)
    print_search_results(releases)

    if releases['release-count'] == 0:
        return None

    selected = select_from_search_results(releases)

    if selected is None:
        return None

    try:
        result = musicbrainzngs.get_release_by_id(selected['id'], includes=['artists', 'recordings', 'artist-credits'])
        return result['release']
    except musicbrainzngs.ResponseError as e:
        print('Failed to look up release MBID %s: %s' % (selected['id'], str(e)))
        return None


def get_from_cache(cache, artist, title):
    data = cache.lookup(artist, title)
    if data is None:
        data = get_from_musicbrainz(artist, title)
        if data is not None:
            cache.store(artist, title, data)

    return data


def main():
    args = parse_args()
    cache = ReleaseCache()
    release_data = get_from_cache(cache, args.artist, args.title)

    if release_data is not None:
        print(release_data)


if __name__ == '__main__':
    main()
