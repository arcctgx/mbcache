# mbcache

A simple cache for MusicBrainz data.

## Features

`mbcache` provides:

* recordings cache
* releases cache
* release disambiguation (allows storing many versions of the same release)
* cache naming (allows creating multiple independent caches per application)
* command-line utilities for adding recordings and releases to cache

## Caveats

Current implementation is not thread-safe.
