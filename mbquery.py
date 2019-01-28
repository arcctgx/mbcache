#!/usr/bin/env python2

import sys
import argparse
import musicbrainzngs
import json
import logging

parser = argparse.ArgumentParser(description="Fetch album data from MusicBrainz")
parser.add_argument("mbid", help="release MBID to fetch data for")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)

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

# get artist and MBID:
# if multiple artists get "artist-credit-phrase", and use MBID of first artist (last.fm seems to be doing that)
# TODO

# get release title:
# we already have release MBID from command line
# TODO

# get all track titles, lenghts and MBIDs:
for medium in release["medium-list"]:
    for track in medium["track-list"]:

        # take the length from the track listing, because
        # it could be accurately set from Disc ID
        length = int(track["length"])
        m = length/1000/60  # FIXME round instead of truncating
        s = length/1000%60  # FIXME round instead of truncating

        recording = track["recording"]

        # prefer track title over recording title
        # (track title exists only if it is different from recording title)
        try:
            title = track["title"]
        except KeyError:
            title = recording["title"]

        print "%s\t%d:%02d (%d)\t%s" % (title, m, s, length, recording["id"])
