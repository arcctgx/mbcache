#!/usr/bin/env python3

import json
import os
from xdg import BaseDirectory

class RecordingCache:
    def __init__(self, application='mbcache', cache_name='recordings', sort_entries=False):
        self.cache = {}
        self.update_required = False
        self.sort_entries = sort_entries
        self.cache_dir = BaseDirectory.save_cache_path(application)
        self.cache_path = os.path.join(self.cache_dir, cache_name + '.json')

        try:
            with open(self.cache_path, 'r') as f:
                self.cache = json.load(f)
            print('Loaded', len(self.cache), 'cache entries.')
        except FileNotFoundError:
            print('Cache file does not exist. Initializing empty cache.')

    def __del__(self):
        if self.update_required:
            with open(self.cache_path, 'w') as f:
                if self.sort_entries:
                    sorted_cache = dict(sorted(self.cache.items(), key=lambda i: i[0]))
                    json.dump(sorted_cache, f, indent=2)
                else:
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
