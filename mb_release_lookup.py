#!/usr/bin/env python3

import argparse
import musicbrainzngs
import entities
from cache import ReleaseCache

def query_album_mbid(album_mbid):

    musicbrainzngs.set_useragent("mbcache", "v0.1.0a")

    try:
        result = musicbrainzngs.get_release_by_id(album_mbid, includes=['artists', 'recordings', 'artist-credits'])
    except musicbrainzngs.ResponseError as e:
        print("Failed to look up release MBID \"%s\" %s" % (album_mbid, str(e)))
        return None

    try:
        release = result["release"]
        return release
    except KeyError:
        print("Query for MBID \"%s\" returned empty result!" % album_mbid)
        return None

def main():
    parser = argparse.ArgumentParser(description="Fetch album data from MusicBrainz")
    parser.add_argument("mbid", help="release MBID to fetch data for")
    args = parser.parse_args()

    cache = ReleaseCache()

    release = query_album_mbid(args.mbid)
    if release:
        cache.store(release['artist-credit-phrase'], release['title'], release)
        album = entities.Album.from_json_release(release)
        print(repr(album))

if __name__ == '__main__':
    main()
