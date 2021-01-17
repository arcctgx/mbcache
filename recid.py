#!/usr/bin/env python3

import argparse
import json
import logging
import musicbrainzngs as mb
import os
import sys
from xdg import BaseDirectory

class Cache:
    __cache_dir = BaseDirectory.save_cache_path('mbcache')
    __cache_file = os.path.join(__cache_dir, 'recording_cache.json')
    __cache = {}
    __modified = False

    def __init__(self):
        try:
            with open(self.__cache_file, 'r') as f:
                self.__cache = json.load(f)
            print('Loaded', len(self.__cache), 'entries from cache.')
        except FileNotFoundError:
            print('Cache file does not exist. Initializing empty cache.')

    def __del__(self):
        if self.__modified:
            with open(self.__cache_file, 'w') as f:
                json.dump(self.__cache, f, indent=2)

    def __str__(self):
        return json.dumps(self.__cache, indent=2)

    @staticmethod
    def __encode_key(artist, title, album):
        return '\t'.join((artist, title, album)).lower()

    def retrieve(self, artist, title, album):
        key = self.__encode_key(artist, title, album)
        return self.__cache.get(key)

    def store(self, artist, title, album, mbid):
        key = self.__encode_key(artist, title, album)
        self.__cache[key] = mbid
        self.__modified = True


def parse_args():
    parser = argparse.ArgumentParser(description='Find recording MBID based on artist, title and album.')
    parser.add_argument('artist', help='artist name')
    parser.add_argument('title', help='recording title')
    parser.add_argument('album', help='album title')

    return parser.parse_args()


def get_recording_mbid(artist, title, album):
    mb.set_useragent('mbcache', 'v0.1.0a')

    recordings = mb.search_recordings(artist=artist, recordingaccent=title, release=album, strict=True)
    #print(json.dumps(recordings, sort_keys=True, indent=2))
    count = recordings['recording-count']

    if count == 0:
        raise ValueError
    elif recordings['recording-count'] == 1:
        print('Search returned a single result:')
        print_candidates(recordings)
        return recordings['recording-list'][0]['id']
    else:
        print('Search returned %d results:' % count)
        print_candidates(recordings)
        return select_recording(recordings)


def print_candidates(recordings):
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

        print("[%d]\tscore = %s\t(%d albums, %d ISRCs)\t%s - \"%s\"%s" %
                (idx+1, score, albums, isrcs, artist, title, disambiguation))


def select_recording(recordings):
    count = recordings['recording-count']
    index = int(input('Which one to use? [1-%d] ' % count))
    if index <= 0 or index > count:
        print("Index %s out of range!" % index)
        sys.exit(1)

    return recordings['recording-list'][index-1]['id']


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()

    recording_cache = Cache()

    mbid = recording_cache.retrieve(args.artist, args.title, args.album)
    if mbid == None:
        try:
            mbid = get_recording_mbid(args.artist, args.title, args.album)
            recording_cache.store(args.artist, args.title, args.album, mbid)
            print(mbid)
        except ValueError:
            print('Search returned no results!')
    else:
        print(mbid)

if __name__ == '__main__':
    main()
