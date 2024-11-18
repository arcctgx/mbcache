"""
This module provides high-level cache objects for direct use by applications.
The included classes manage searching for entities in MusicBrainz, displaying
search results to users, and handling storage and retrieval operations via
low-level cache objects.

The caches are protected against concurrent access by different processes, but
not by multiple threads within one process. It is the responsibility of the
user to ensure thread-level synchronization.
"""

import musicbrainzngs

from mbcache.cache import _RecordingCache, _ReleaseCache
from mbcache.params import _RecordingParams, _ReleaseParams
from mbcache.version import APPNAME, URL, VERSION


# pylint: disable=too-few-public-methods
class _MbCache:
    """Base class for entity-specific high-level cache objects."""

    def __init__(self):
        musicbrainzngs.set_useragent(APPNAME, VERSION, URL)


# pylint: disable=too-few-public-methods
class MbRecordingCache(_MbCache):
    """
    High-level cache object for MusicBrainz recording MBIDs. Manages searching
    for recording MBIDs in MusicBrainz, presenting search results to the user,
    storing results in the low-level cache, and retrieving them as needed.
    """

    def __init__(self, application=APPNAME, cache_name='recordings'):
        self._cache = _RecordingCache(application, cache_name)
        super().__init__()

    @staticmethod
    def _print_search_results(recordings):
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

    @staticmethod
    def _select_from_search_results(recordings):
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

    @staticmethod
    def _search_in_musicbrainz(artist, title, album):
        recordings = musicbrainzngs.search_recordings(artist=artist,
                                                      recordingaccent=title,
                                                      release=album,
                                                      video=False,
                                                      strict=True)

        MbRecordingCache._print_search_results(recordings)

        if recordings['recording-count'] == 0:
            return None

        return MbRecordingCache._select_from_search_results(recordings)

    def get(self, artist, title, album):
        """
        Retrieve a recording from the cache using the specified artist, title,
        and album information. If the recording is not found in the cache,
        search for it in MusicBrainz and add it to the cache for future use.
        If the search result is ambiguous, present the choices to the user
        and ask them to select the best-matching recording.
        """
        params = _RecordingParams(artist, title, album)

        mbid = self._cache.lookup(params)
        if mbid is not None:
            return mbid

        mbid = self._search_in_musicbrainz(artist, title, album)
        if mbid is not None:
            self._cache.store(mbid, params)

        return mbid


class MbReleaseCache(_MbCache):
    """
    High-level cache object for MusicBrainz releases. Manages searching for
    releases in MusicBrainz, presenting search results to the user, storing
    the results in the low-level cache, and retrieving them by artist and
    title, or by release MBID.
    """

    def __init__(self, application=APPNAME, cache_name='releases'):
        self._cache = _ReleaseCache(application, cache_name)
        super().__init__()

    @staticmethod
    def _print_search_results(releases):
        count = releases['release-count']

        if count == 0:
            print('Search returned no results!')
        elif count == 1:
            print('Search returned a single result:')
        else:
            print(f'Search returned {count} results:')

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

            not_empty = [piece for piece in info if piece]
            print('[%d]\tscore = %s\t%s - "%s" (%s)%s' %
                  (idx + 1, score, artist, title, ', '.join(not_empty), disambiguation))

    @staticmethod
    def _select_from_search_results(releases):
        count = releases['release-count']

        if count == 1:
            return releases['release-list'][0]

        while True:
            index = int(input(f'Which one to use? (0 - none of these) [0-{count}] '))

            if index == 0:
                print('Search result discarded.')
                return None

            if 1 <= index <= count:
                return releases['release-list'][index - 1]

    @staticmethod
    def _search_in_musicbrainz(artist, title):
        releases = musicbrainzngs.search_releases(artist=artist, releaseaccent=title, strict=True)
        MbReleaseCache._print_search_results(releases)

        if releases['release-count'] == 0:
            return None

        selected = MbReleaseCache._select_from_search_results(releases)

        if selected is None:
            return None

        try:
            result = musicbrainzngs.get_release_by_id(
                selected['id'], includes=['artists', 'recordings', 'artist-credits'])
            return result['release']
        except musicbrainzngs.ResponseError as exc:
            print(f'Failed to look up release MBID {selected["id"]}: {exc}')
            return None

    @staticmethod
    def _lookup_in_musicbrainz(album_mbid):
        try:
            result = musicbrainzngs.get_release_by_id(
                album_mbid, includes=['artists', 'recordings', 'artist-credits'])
        except musicbrainzngs.ResponseError as exc:
            print(f'Failed to look up release MBID {album_mbid}: {exc}')
            return None

        try:
            return result['release']
        except KeyError:
            print(f'Query for MBID {album_mbid} returned empty result!')
            return None

    def get(self, artist, title, disambiguation=None):
        """
        Retrieve a release from the cache using the specified artist, title,
        and an optional disambiguation string. If the release is not found in
        the cache, search for it in MusicBrainz and add it to the cache for
        future use. If the search result is ambiguous, present the choices to
        the user and ask them to select the best-matching release.
        """
        params = _ReleaseParams(artist, title, disambiguation)

        release = self._cache.lookup(params)
        if release is not None:
            return release

        release = self._search_in_musicbrainz(artist, title)
        if release is not None:
            self._cache.store(release, params)

        return release

    def get_mbid(self, mbid, disambiguation=None):
        """
        Retrieve a release from the cache using the specified release MBID. If
        the release is not found, look it up in MusicBrainz using the MBID and
        add it to the cache for future use. The artist and title used to create
        the cache key are extracted from the release data retrieved by the MBID.
        The optional disambiguation string parameter is used only for storing
        the release in the cache.
        """
        release = self._cache.lookup_id(mbid)
        if release is not None:
            return release

        release = self._lookup_in_musicbrainz(mbid)
        if release is not None:
            params = _ReleaseParams(release['artist-credit-phrase'], release['title'],
                                    disambiguation)
            self._cache.store(release, params)

        return release
