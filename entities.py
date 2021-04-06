class Artist:
    """
    MusicBrainz artist entity.
    attributes: name, mbid
    """
    def __init__(self, name, mbid):
        self.name = name
        self.mbid = mbid

    def __repr__(self):
        return '%s\t%s' % (self.name, self.mbid)


class Track:
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
        return '%s\t%s\t%s' % (self.title, self.time_base_60, self.mbid)

    def to_seconds(self, minsec):
        m, s = minsec.split(':')
        return 60*int(m) + int(s)


class Release:
    """
    Musicbrainz release entity.
    attributes: title, mbid
    """
    def __init__(self, title, mbid):
        self.title = title
        self.mbid = mbid

    def __repr__(self):
        return '%s\t%s' % (self.title, self.mbid)


class Album:
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

    @classmethod
    def from_json_release(cls, release):
        # use MBID of first artist even in case of multiple artists
        # (last.fm seems to be doing that)
        art = Artist(
            release["artist-credit-phrase"],
            release["artist-credit"][0]["artist"]["id"]
        )

        rel = Release(
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

                tr = Track(
                    title,
                    track["recording"]["id"],
                    time
                )
                tracks.append(tr)

        return cls(art, rel, tracks)
