"""
Provides a file-based locking mechanism for POSIX-compliant systems.

The implementation ensures exclusive access across multiple OS processes with
fcntl locking mechanism, allowing only one process at a time to hold the lock.
Because of fcntl dependency, the implementation works only on POSIX-compliant
operating systems.

Note: this lock does not prevent concurrent access by multiple threads in the
same process.
"""

import fcntl


class _Lock:
    """An exclusive, reentrant, inter-process lock."""

    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.lock_file = None

    def acquire(self):
        """
        Acquire the lock for exclusive access across processes.

        This method blocks if the lock is held by another process, but will
        not block if the lock is already held by the same process. This means
        the lock will not prevent concurrent access by multiple threads in the
        same process.
        """
        self.lock_file = open(self.lock_path, 'ab')  # pylint: disable=consider-using-with
        fcntl.flock(self.lock_file, fcntl.LOCK_EX)

    def release(self):
        """
        Release the lock.

        This method safely releases the lock, even if called multiple times by
        the same process. It has no effect if the lock is not currently held by
        the process.
        """
        if self.lock_file is None:
            return

        fcntl.flock(self.lock_file, fcntl.LOCK_UN)
        self.lock_file.close()
        self.lock_file = None
