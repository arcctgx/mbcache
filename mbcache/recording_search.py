"""Find recording MBID based on artist, title and album."""

import argparse
import musicbrainzngs
from mbcache import RecordingCache, APPNAME, VERSION, URL


def parse_args():
    parser = argparse.ArgumentParser(
        description='Find recording MBID based on artist, title and album.')
    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='recording title')
    parser.add_argument('album', help='album title')
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def print_search_results(recordings):
    count = recordings['recording-count']

    if count == 0:
        print('Search returned no results!')
    elif count == 1:
        print('Search returned a single result:')
    else:
        print(f'Search returned {count} results:')

    for (idx, recording) in enumerate(recordings['recording-list']):
        score = recording['ext:score']
        artist = recording['artist-credit-phrase']
        title = recording['title']
        albums = len(recording['release-list'])

        try:
            disambiguation = ' (' + recording['disambiguation'] + ')'
        except KeyError:
            disambiguation = ''

        try:
            isrcs = len(recording['isrc-list'])
        except KeyError:
            isrcs = 0

        print('[%d]\tscore = %s\t(%d releases, %d ISRCs)\t%s - "%s"%s' %
              (idx + 1, score, albums, isrcs, artist, title, disambiguation))


def select_from_search_results(recordings):
    count = recordings['recording-count']

    if count == 1:
        return recordings['recording-list'][0]['id']

    while True:
        index = int(input(f'Which one to use? (0 - none of these) [0-{count}] '))

        if index == 0:
            print('Search result discarded.')
            return None

        if 1 <= index <= count:
            return recordings['recording-list'][index - 1]['id']


def get_from_musicbrainz(artist, title, album):
    musicbrainzngs.set_useragent(APPNAME, VERSION, URL)

    recordings = musicbrainzngs.search_recordings(artist=artist,
                                                  recordingaccent=title,
                                                  release=album,
                                                  video=False,
                                                  strict=True)

    print_search_results(recordings)

    if recordings['recording-count'] == 0:
        return None

    return select_from_search_results(recordings)


def get_from_cache(cache, artist, title, album):
    mbid = cache.lookup(artist, title, album)
    if mbid is None:
        mbid = get_from_musicbrainz(artist, title, album)
        if mbid is not None:
            cache.store(artist, title, album, mbid)

    return mbid


def main():
    args = parse_args()
    cache = RecordingCache()
    mbid = get_from_cache(cache, args.artist, args.title, args.album)

    if mbid is not None:
        print(mbid)


if __name__ == '__main__':
    main()
