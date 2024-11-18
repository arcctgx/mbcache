"""Entity parameters module."""

from dataclasses import dataclass
from typing import Optional

from mbnames import normalize


@dataclass
class _EntityParams:
    """Abstract base class for entity parameters."""

    def key(self) -> str:
        """Represent entity parameters as a cache key."""
        raise NotImplementedError


@dataclass
class _RecordingParams(_EntityParams):
    """Recording parameters."""
    artist: str
    title: str
    album: str

    def key(self) -> str:
        """Represent recording parameters as a cache key."""
        return normalize('\t'.join((self.artist, self.album, self.title)))


@dataclass
class _ReleaseParams(_EntityParams):
    """Release parameters."""
    artist: str
    title: str
    disambiguation: Optional[str]

    def key(self) -> str:
        """Represent release parameters as a cache key."""
        if self.disambiguation is None:
            return normalize('\t'.join((self.artist, self.title)))

        return normalize('\t'.join((self.artist, self.title, self.disambiguation)))
