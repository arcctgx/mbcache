#!/usr/bin/env python2

import sys
import argparse
import musicbrainzngs
#import json
#import logging
import entities

parser = argparse.ArgumentParser(description="Fetch album data from MusicBrainz")
parser.add_argument("mbid", help="release MBID to fetch data for")
args = parser.parse_args()

#logging.basicConfig(level=logging.DEBUG)

musicbrainzngs.set_useragent("mbcache", "v0.1.0a")

try:
    result = musicbrainzngs.get_release_by_id(args.mbid, includes=["artists", "recordings"])
except musicbrainzngs.ResponseError as e:
    sys.exit("Failed to look up release MBID \"%s\" %s" % (args.mbid, str(e)))

#print json.dumps(result, sort_keys=True, indent=2)

try:
    release = result["release"]
except KeyError:
    sys.exit("Query for MBID \"%s\" returned empty result!" % args.mbid)

# use MBID of first artist even in case of multiple artists
# (last.fm seems to be doing that)
art = entities.Artist(
    release["artist-credit-phrase"],
    release["artist-credit"][0]["artist"]["id"]
)
print repr(art)

rel = entities.Release(
    release["title"],
    release["id"]
)
print repr(rel)

# get all track titles, lenghts and MBIDs:
tracks = []

for medium in release["medium-list"]:
    for track in medium["track-list"]:

        # prefer track length over recording length, because
        # track length could be accurately set from Disc ID
        len_ms = float(track["length"])
        len_sec = round(len_ms/1000, 0)
        m = len_sec / 60
        s = len_sec % 60

        # prefer track title over recording title
        # (track title exists only if it is different from recording title)
        try:
            title = track["title"]
        except KeyError:
            title = track["recording"]["title"]

        tr = entities.Track(
            title,
            track["recording"]["id"],
            "%d:%02d" % (m,s)
        )
        tracks.append(tr)
        print repr(tr)
