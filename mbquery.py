#!/usr/bin/env python

import sys
import musicbrainzngs

musicbrainzngs.set_useragent("mbcache", "v0.1.0a")

artist = sys.argv[1]
album = sys.argv[2]

print "querying %s -- \"%s\"" % (artist, album)

result = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)

if not result['release-list']:
    sys.exit("no release found")
else:
    print result
