#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import tempfile

class FileSystem(object):
    def exists(self, path):
        return os.path.exists(path)

    def makedirs(self, path):
        os.makedirs(path)

    def tempfile(self, directory):
        return tempfile.mkstemp(dir=directory)

    def write(self, f, content):
        os.write(f, content)

    def close(self, f):
        os.close(f)

    def chmod(self, filename, flags):
        os.chmod(filename, flags)

    def rename(self, from_file, to_file):
        os.rename(tmpname, filename)

    def remove(self, path):
        os.remove(path)

    def rmdir(self, directory):
        os.rmdir(directory)
        
    def join(self, root, path):
        return os.path.join(root, path.lstrip('/'))
        
    def dirname(self, path):
        return os.path.dirname(path)

