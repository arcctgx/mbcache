#!/usr/bin/env python3

import argparse
import json
import logging
import musicbrainzngs as mb
import os
import sys
from xdg import BaseDirectory

class RecordingCache:
    def __init__(self):
        self.cache = {}
        self.update_required = False
        self.dir_path = BaseDirectory.save_cache_path('mbcache')
        self.file_path = os.path.join(self.dir_path, 'recording_cache.json')

        try:
            with open(self.file_path, 'r') as f:
                self.cache = json.load(f)
            print('Loaded', len(self.cache), 'cache entries.')
        except FileNotFoundError:
            print('Cache file does not exist. Initializing empty cache.')

    def __del__(self):
        if self.update_required:
            with open(self.file_path, 'w') as f:
                json.dump(self.cache, f, indent=2)

    def __str__(self):
        return json.dumps(self.cache, indent=2)

    @staticmethod
    def encode_key(artist, title, album):
        return '\t'.join((artist, album, title)).lower()

    def lookup(self, artist, title, album):
        key = self.encode_key(artist, title, album)
        return self.cache.get(key)

    def store(self, artist, title, album, mbid):
        key = self.encode_key(artist, title, album)
        self.cache[key] = mbid
        self.update_required = True


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

    cache = RecordingCache()

    mbid = cache.lookup(args.artist, args.title, args.album)
    if mbid == None:
        try:
            mbid = get_recording_mbid(args.artist, args.title, args.album)
            cache.store(args.artist, args.title, args.album, mbid)
        except ValueError:
            print('Search returned no results!')

    if mbid != None:
        print(mbid)

if __name__ == '__main__':
    main()
