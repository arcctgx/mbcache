class Artist(object):
    """
    MusicBrainz artist entity.
    attributes: name, mbid
    """
    def __init__(self, name, mbid):
        self.name = name
        self.mbid = mbid

    def __repr__(self):
        s = '%s\t%s' % (self.name, self.mbid)
        return s.encode('utf-8')


class Track(object):
    """
    MusicBrainz recording entity.
    attributes: title, mbid, time_base_60, time_seconds
    """
    def __init__(self, title, mbid, time_base_60='0:00'):
        self.title = title
        self.mbid = mbid
        self.time_base_60 = time_base_60
        self.time_seconds = self.to_seconds(time_base_60)

    def __repr__(self):
        s = '%s\t%s\t%s' % (self.title, self.time_base_60, self.mbid)
        return s.encode('utf-8')

    def to_seconds(self, minsec):
        m, s = minsec.split(':')
        return 60*int(m) + int(s)


class Release(object):
    """
    Musicbrainz release entity.
    attributes: title, mbid
    """
    def __init__(self, title, mbid):
        self.title = title
        self.mbid = mbid

    def __repr__(self):
        s = '%s\t%s' % (self.title, self.mbid)
        return s.encode('utf-8')


class Album(object):
    """
    MusicBrainz album entity.
    attributes: artist, title, mbid, tracklist
    """
    def __init__(self, artist, release, tracklist):
        self.artist = artist
        self.release = release
        self.tracklist = tracklist
        self.title = release.title
        self.mbid = release.mbid

    def __repr__(self):
        s = []
        s.append(repr(self.artist))
        s.append(repr(self.release))
        for track in self.tracklist:
            s.append(repr(track))
        return '\n'.join(s)
