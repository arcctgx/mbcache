# mbcache

[![MusicBrainz](https://img.shields.io/badge/built_with-MusicBrainz-BA478F?logo=musicbrainz)](https://musicbrainz.org)

A simple cache for MusicBrainz data.

## Features

`mbcache` provides:

* recordings cache
* releases cache
* release disambiguation (allows storing many versions of the same release)
* cache naming (allows creating multiple independent caches per application)
* command-line utilities for adding recordings and releases to cache

## Restrictions

Built-in locking mechanism protects against concurrent access by different
processes, but not by threads within one process. It is the responsibility
of the user to ensure thread-level synchronization.

Only POSIX-compliant operating systems are supported.
