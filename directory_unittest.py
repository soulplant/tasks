from __future__ import with_statement

from directory import Directory
import os
import unittest
import shutil

class DirectoryTest(unittest.TestCase):
    def setUp(self):
        os.mkdir('temp')
        os.mkdir('temp/dir1')
        with open('temp/dir1/meta', 'w') as f:
            f.write('name:test')
        os.mkdir('temp/dir2')
        os.mkdir('temp/dir1/a')
        self.d = Directory('temp')

    def tearDown(self):
        shutil.rmtree('temp')

    def assertDirNames(self, names, dirs):
        self.assertEquals(names, map(lambda d: d.name(), dirs))

    def test_writelines(self):
        lines = ['Name:Blah']
        self.d.writelines('meta', lines)
        self.assertEquals(lines, self.d.readlines('meta'))

    def test_appendline(self):
        self.d.appendline('log', 'blah')

        self.assertEquals(['blah'], self.d.readlines('log'))
        self.d.appendline('log', 'other')
        self.assertEquals(['blah', 'other'], self.d.readlines('log'))

    def test_directories(self):
        self.assertDirNames(['dir1', 'dir2'], self.d.directories())
        d2 = self.d.directory('dir1')
        self.assertDirNames(['a'], d2.directories())

    def test_make(self):
        nd = self.d.directory('new-dir')
        nd.make()
        self.assertTrue(os.path.isdir('temp/new-dir'))

    def test_name(self):
        self.assertEquals('temp', self.d.name())
        self.assertEquals('dir1', self.d.directory('dir1').name())

    def test_write_directory_implies_make(self):
        asdf = self.d.directory('asdf')
        asdf.writelines('some-file', ['a'])
        self.assertTrue(os.path.isfile('temp/asdf/some-file'))

    def test_path(self):
        self.assertEquals('temp/', self.d.path())
        self.assertEquals('temp/blah/', self.d.directory('blah').path())

    def test_readlines(self):
        self.assertEquals(['name:test'], self.d.directory('dir1').readlines('meta'))

    def test_no_share_path(self):
        d = self.d.directory('temp')
        self.assertEquals('temp/temp/', d.path())
        self.assertEquals('temp/', self.d.path())

    def test_directories_path(self):
        self.assertEquals('temp/dir1/', self.d.directories()[0].path())

if __name__ == '__main__':
    unittest.main()
