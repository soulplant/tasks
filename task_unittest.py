import unittest
from task import Task

class FakeFileSystem(object):
    def __init__(self, name):
        self._name = name
        self._files = {}

    def add_file(self, name, contents):
        self._files[name] = contents

    def readlines(self, name):
        return self._files[name].split('\n')
    
    def writelines(self, name, lines):
        self._files[name] = "\n".join(lines)

    def appendline(self, name, line):
        if len(self._files[name]) == 0:
            self._files[name] = line
        else:
            self._files[name] += "\n%s" % line

    def name(self):
        return self._name
class TaskTest(unittest.TestCase):
    def setUp(self):
        self.f = FakeFileSystem('abc123')
        self.f.add_file('meta', "name:This is a test\nsomething-else:Blah")
        self.f.add_file('log', "Wed Mar  2 20:49:11 2011\tLog entry 1")
        self._load_task()

    def _load_task(self):
        self.t = Task(self.f)

    def test_reads_name_correctly(self):
        self.assertEquals('This is a test', self.t.name())

    def test_writes_name_correctly(self):
        self.t.set_name('New name')
        self.assertEquals('New name', self.t.name())
        self.t.save()
        self._load_task()
        self.assertEquals('New name', self.t.name())

    def test_reads_logs(self):
        self.assertEquals(1, len(self.t.log()))

    def test_appends_logs(self):
        self.t.add_to_log('Woo!')
        self._load_task()
        self.assertEquals(2, len(self.t.log()))

if __name__ == "__main__":
    unittest.main()
