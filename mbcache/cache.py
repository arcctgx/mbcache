"""A simple cache for storing MusicBrainz recordings and releases."""

import glob
import json
import os
import time

from mbnames import normalize
from xdg import BaseDirectory


class _RecordingCache:
    """
    Cache for storing recording MBIDs.

    Cache is stored in JSON file in user's XDG cache directory. The path is
    derived from application name and cache name, passed as arguments to the
    class constructor.

    Objects are stored in key-value format, where the key is derived from
    artist name, track title and album title, and the value is the recording
    MBID.

    Cache stores times of last update and last lookup as UNIX timestamps.
    """

    def __init__(self, application, cache_name, sort_index=False):
        self.cache = {}
        self.update_required = False
        self.sort_index = sort_index
        self.cache_dir = BaseDirectory.save_cache_path(application)
        self.cache_path = os.path.join(self.cache_dir, cache_name + '.json')

        try:
            with open(self.cache_path, encoding='utf-8') as cache_file:
                self.cache = json.load(cache_file)
            print('Loaded', len(self.cache), 'cache entries.')
        except FileNotFoundError:
            print('Cache file does not exist. Initializing empty cache.')

    def __del__(self):
        if self.update_required:
            with open(self.cache_path, 'w', encoding='utf-8') as cache_file:
                json.dump(self.cache, cache_file, indent=1, sort_keys=self.sort_index)

    def __str__(self):
        return json.dumps(self.cache, indent=1)

    @staticmethod
    def _encode_key(artist, title, album):
        return normalize('\t'.join((artist, album, title)))

    def lookup(self, artist, title, album):
        """Look up a recording MBID by artist, title and album."""
        key = self._encode_key(artist, title, album)
        try:
            entry = self.cache[key]
            entry['last_lookup'] = int(time.time())
            self.update_required = True
            return entry['id']
        except KeyError:
            return None

    def store(self, artist, title, album, mbid):
        """Store a recording MBID in cache."""
        key = self._encode_key(artist, title, album)
        value = {'id': mbid, 'last_update': int(time.time()), 'last_lookup': None}
        self.cache[key] = value
        self.update_required = True


class _ReleaseCache:
    """
    Cache for storing MusicBrainz release data.

    Cache is stored in user's XDG cache directory, in subdirectory whose path
    is derived from application name and cache name passed as arguments to the
    class constructor. It contains JSON files with release data, whose names
    are derived from MusicBrainz release MBIDs. It additionally contains a
    key-value index file, which maps keys to release MBIDs.

    Index keys are derived from artist names and release titles, which must be
    unique. To make it possible to keep multiple versions of the same album in
    cache, an optional disambiguation string can be provided to distinguish
    otherwise identically named releases. If disambiguation string is not
    provided when another release with the same name artist and title is stored
    in cache, the cache entry will be replaced and old release JSON file will
    be removed.

    Cache stores times of last update and last lookup as UNIX timestamps. Also
    stored is the permanence information. If cache entry is set as permanent,
    it will never be invalidated or updated automatically (but can still be
    replaced as described above).
    """

    def __init__(self, application, cache_name, sort_index=False):
        self.cache = None
        self.update_required = False
        self.sort_index = sort_index
        self.cache_dir = BaseDirectory.save_cache_path(application, cache_name)
        self.index_path = os.path.join(self.cache_dir, 'index.json')

        try:
            with open(self.index_path, encoding='utf-8') as cache_index:
                self.cache = json.load(cache_index)
            print('Loaded', len(self.cache), 'cache entries.')
        except FileNotFoundError:
            self.cache = {}
            print('Cache index does not exist. Initialized empty cache.')

    def __del__(self):
        if self.cache is not None:
            if self.update_required:
                with open(self.index_path, 'w', encoding='utf-8') as cache_index:
                    json.dump(self.cache, cache_index, indent=1, sort_keys=self.sort_index)

            self._remove_orphans()

    def __str__(self):
        return json.dumps(self.cache, indent=1)

    def _remove_orphans(self):
        in_cache = set(
            glob.glob(os.path.join(self.cache_dir, '????????-????-????-????-????????????.json')))
        in_index = {
            os.path.join(self.cache_dir, entry['id'] + '.json')
            for entry in self.cache.values()
        }
        orphans = in_cache - in_index
        num_orphans = len(orphans)

        for i in orphans:
            os.remove(i)

        if num_orphans > 0:
            print('Removed', num_orphans, 'orphaned cache files.')

    @staticmethod
    def _encode_key(artist, title, disambiguation=None):
        if disambiguation is None:
            return normalize('\t'.join((artist, title)))

        return normalize('\t'.join((artist, title, disambiguation)))

    def lookup(self, artist, title, disambiguation=None):
        """
        Look up release data by artist, title
        and optional disambiguation string.
        """
        key = self._encode_key(artist, title, disambiguation)
        try:
            entry = self.cache[key]
            entry['last_lookup'] = int(time.time())
            self.update_required = True
        except KeyError:
            return None

        mbid = entry['id']
        release_file = os.path.join(self.cache_dir, mbid + '.json')

        try:
            with open(release_file, encoding='utf-8') as rel:
                return json.load(rel)
        except FileNotFoundError:
            return None

    def lookup_id(self, mbid):
        """Look up release information by MBID."""
        index_mbids = [entry['id'] for entry in self.cache.values()]
        if mbid not in index_mbids:
            return None

        rev_index = {val['id']: key for key, val in self.cache.items()}
        mbid_key = rev_index[mbid]
        self.cache[mbid_key]['last_lookup'] = int(time.time())
        self.update_required = True

        release_file = os.path.join(self.cache_dir, mbid + '.json')

        try:
            with open(release_file, encoding='utf-8') as rel:
                return json.load(rel)
        except FileNotFoundError:
            return None

    def store(self, artist, title, release_data, disambiguation=None):
        """Store release data in cache, with optional disambiguation string."""
        mbid = release_data['id']
        key = self._encode_key(artist, title, disambiguation)
        value = {
            'id': mbid,
            'last_update': int(time.time()),
            'last_lookup': None,
            'permanent': False
        }
        self.cache[key] = value
        self.update_required = True

        release_file = os.path.join(self.cache_dir, mbid + '.json')

        with open(release_file, 'w', encoding='utf-8') as rel:
            json.dump(release_data, rel, indent=1)
