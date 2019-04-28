#!/usr/bin/env python2

import sys
import argparse
import musicbrainzngs
#import json
#import logging
import entities

def query_album_mbid(album_mbid):
    #logging.basicConfig(level=logging.DEBUG)

    musicbrainzngs.set_useragent("mbcache", "v0.1.0a")

    try:
        result = musicbrainzngs.get_release_by_id(album_mbid, includes=["artists", "recordings"])
    except musicbrainzngs.ResponseError as e:
        print "Failed to look up release MBID \"%s\" %s" % (album_mbid, str(e))
        return None

    #print json.dumps(result, sort_keys=True, indent=2)

    try:
        release = result["release"]
        return release
    except KeyError:
        print "Query for MBID \"%s\" returned empty result!" % album_mbid
        return None

def parse_release_data(release):
    # use MBID of first artist even in case of multiple artists
    # (last.fm seems to be doing that)
    art = entities.Artist(
        release["artist-credit-phrase"],
        release["artist-credit"][0]["artist"]["id"]
    )

    rel = entities.Release(
        release["title"],
        release["id"]
    )

    # get all track titles, lenghts and MBIDs:
    tracks = []

    for medium in release["medium-list"]:
        for track in medium["track-list"]:

            # prefer track length over recording length, because
            # track length could be accurately set from Disc ID
            try:
                len_ms = float(track["length"])
                len_sec = round(len_ms/1000, 0)
                time = "%d:%02d" % (len_sec/60, len_sec%60)
            except KeyError:
                time = "0:00"

            # prefer track title over recording title
            # (track title exists only if it is different from recording title)
            try:
                title = track["title"]
            except KeyError:
                title = track["recording"]["title"]

            tr = entities.Track(
                title,
                track["recording"]["id"],
                time
            )
            tracks.append(tr)

    return entities.Album(art, rel, tracks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch album data from MusicBrainz")
    parser.add_argument("mbid", help="release MBID to fetch data for")
    args = parser.parse_args()

    release = query_album_mbid(args.mbid)
    if release:
        album = parse_release_data(release)
        print repr(album)
