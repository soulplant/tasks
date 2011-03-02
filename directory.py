from __future__ import with_statement

import glob
import os

class Directory(object):
    def __init__(self, path):
        self._path = path
        if not self._path.endswith(os.path.sep):
            self._path += os.path.sep

    def _open(self, name, mode):
        return open(os.path.join(self._path, name), mode)

    def _isfile(self, name):
        return os.path.isfile(os.path.join(self._path, name))

    def make(self):
        if not os.path.isdir(self._path):
            os.mkdir(self._path)

    def readlines(self, name):
        if self._isfile(name):
            with self._open(name, 'r') as f:
                return [l.rstrip() for l in f.readlines()]
        return []

    def writelines(self, name, lines):
        self.make()
        with self._open(name, 'w') as f:
            f.write("\n".join(lines))

    def appendline(self, name, line):
        if len(self.readlines(name)) == 0:
            self.writelines(name, [line])
            return
        with self._open(name, 'a') as f:
            f.write("\n%s" % line)

    def directories(self):
        pattern = os.path.join(self._path, '*')
        result = []
        for f in glob.glob(pattern):
            if os.path.isdir(f):
                result.append(Directory(f))
        return result
    
    def directory(self, dirname):
        return Directory(os.path.join(self._path, dirname))
    
    def name(self):
        return os.path.basename(self._path.rstrip(os.path.sep))

    def path(self):
        return self._path
