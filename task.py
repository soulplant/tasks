import time

class Task(object):
    def __init__(self, directory):
        self._directory = directory
        self._task_id = directory.name()
        self._meta = self._parse_meta(directory.readlines('meta'))

    def _parse_meta(self, lines):
        meta = {}
        for line in lines:
            k, v = line.split(':')
            meta[k] = v
        return meta
    
    def _unparse_meta(self, meta):
        return ["%s:%s" % (k, meta[k]) for k in meta]
    
    def save(self):
        self._directory.writelines('meta', self._unparse_meta(self._meta))

    def name(self):
        return self._meta['name']

    def set_name(self, name):
        self._meta['name'] = name

    def add_to_log(self, message):
        entry = time.asctime() + "\t" + message
        self._directory.appendline('log', entry)

    def log(self):
        lines = self._directory.readlines('log')
        result = []
        for l in lines:
            t, message = l.split('\t')
            result.append((time.strptime(t), message))
        return result
