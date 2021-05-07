#!/usr/bin/env python3

import glob
import json
import os
import time
from xdg import BaseDirectory

class RecordingCache:
    def __init__(self, application='mbcache', cache_name='recordings', sort_index=False):
        self.cache = {}
        self.update_required = False
        self.sort_index = sort_index
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
                json.dump(self.cache, f, indent=1, sort_keys=self.sort_index)

    def __str__(self):
        return json.dumps(self.cache, indent=1)

    @staticmethod
    def encode_key(artist, title, album):
        return '\t'.join((artist, album, title)).lower()

    def lookup(self, artist, title, album):
        key = self.encode_key(artist, title, album)
        try:
            entry = self.cache[key]
            entry['last_lookup'] = int(time.time())
            self.update_required = True
            return entry['id']
        except KeyError:
            return None

    def store(self, artist, title, album, mbid):
        key = self.encode_key(artist, title, album)
        value = {
            'id': mbid,
            'last_update': int(time.time()),
            'last_lookup': None
        }
        self.cache[key] = value
        self.update_required = True


class ReleaseCache:
    def __init__(self, application='mbcache', cache_name='releases', sort_index=False):
        self.cache = None
        self.update_required = False
        self.sort_index = sort_index
        self.cache_dir = BaseDirectory.save_cache_path(application, cache_name)
        self.index_path = os.path.join(self.cache_dir, 'index.json')

        try:
            with open(self.index_path) as f:
                self.cache = json.load(f)
            print('Loaded', len(self.cache), 'cache entries.')
        except FileNotFoundError:
            self.cache = dict()
            print('Cache index does not exist. Initialized empty cache.')

    def __del__(self):
        if self.cache is not None:
            if self.update_required:
                with open(self.index_path, 'w') as f:
                    json.dump(self.cache, f, indent=1, sort_keys=self.sort_index)

            self.remove_orphans()

    def __str__(self):
        return json.dumps(self.cache, indent=1)

    def remove_orphans(self):
        in_cache = set(glob.glob(os.path.join(self.cache_dir, '????????-????-????-????-????????????.json')))
        in_index = set([os.path.join(self.cache_dir, entry['id'] + '.json') for entry in self.cache.values()])
        orphans = in_cache - in_index
        num_orphans = len(orphans)

        for i in orphans:
            os.remove(i)

        if num_orphans > 0:
            print('Removed', num_orphans, 'orphaned cache files.')

    @staticmethod
    def encode_key(artist, title):
        return '\t'.join((artist, title)).lower()

    def lookup(self, artist, title):
        key = self.encode_key(artist, title)
        try:
            entry = self.cache[key]
            entry['last_lookup'] = int(time.time())
            self.update_required = True
        except KeyError:
            return None

        mbid = entry['id']
        release_file = os.path.join(self.cache_dir, mbid + '.json')

        try:
            with open(release_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def lookup_id(self, mbid):
        index_mbids = [entry['id'] for entry in self.cache.values()]
        if mbid not in index_mbids:
            return None

        rev_index = {val['id']: key for key, val in self.cache.items()}
        mbid_key = rev_index[mbid]
        self.cache[mbid_key]['last_lookup'] = int(time.time())
        self.update_required = True

        release_file = os.path.join(self.cache_dir, mbid + '.json')

        try:
            with open(release_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def store(self, artist, title, release_data):
        mbid = release_data['id']
        key = self.encode_key(artist, title)
        value = {
            'id': mbid,
            'last_update': int(time.time()),
            'last_lookup': None
        }
        self.cache[key] = value
        self.update_required = True

        release_file = os.path.join(self.cache_dir, mbid + '.json')

        with open(release_file, 'w') as f:
            json.dump(release_data, f, indent=0)
