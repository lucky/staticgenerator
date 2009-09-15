#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from os.path import abspath, join, dirname, exists
import tempfile

from staticgenerator.staticgenerator import FileSystem

ROOT_DIR = join(abspath(os.curdir), "test_data")

def test_can_create_filesystem():
    fs = FileSystem()

    assert fs
    assert isinstance(fs, FileSystem)

def test_current_directory_exists():
    fs = FileSystem()
    assert fs.exists(ROOT_DIR)

def test_directory_not_exists():
    fs = FileSystem()
    assert not fs.exists('/fake/dir')

def test_can_create_directory():
    fs = FileSystem()

    path = join(ROOT_DIR, "test")

    fs.makedirs(path)

    assert exists(path)

    os.rmdir(path)

def test_can_create_tempfile():
    fs = FileSystem()

    temp_file = fs.tempfile(ROOT_DIR)

    assert len(temp_file) == 2

    os.remove(temp_file[1])

def test_can_write_content_in_tempfile():
    fs = FileSystem()

    temp_file = tempfile.mkstemp()
    bytes = fs.write(temp_file[0], "foo")

    assert bytes == 3

def test_can_close_tempfile():
    fs = FileSystem()

    temp_file = tempfile.mkstemp()
    fs.close(temp_file[0])

    try:
        fs.close(temp_file[0])
        assert False
    except OSError:
        pass

def test_can_rename_file():
    fs = FileSystem()

    file_path = join(ROOT_DIR, "some_file")
    f = open(file_path, "w")
    f.write("content")
    f.close()

    new_file_path = join(ROOT_DIR, "new_file")
    fs.rename(file_path, new_file_path)

    f = open(new_file_path, "r")
    assert f.read() == "content"

    f.close()

def test_can_remove_file():
    fs = FileSystem()

    file_path = join(ROOT_DIR, "some_file")
    f = open(file_path, "w")
    f.write("content")
    f.close()

    fs.remove(file_path)

    assert not exists(file_path)

def test_can_remove_dir():
    fs = FileSystem()

    dir_path = join(ROOT_DIR, "some_dir")
    os.mkdir(dir_path)

    fs.rmdir(dir_path)

    assert not exists(dir_path)

def test_join_many_paths():
    fs = FileSystem()
    assert fs.join("/fake", "/dir", "/other") == "/fake/dir/other"

def test_join_single_path():
    fs = FileSystem()
    assert fs.join("/fake") == "/fake"

def test_join_two_paths():
    fs = FileSystem()
    assert fs.join("/fake", "/dir") == "/fake/dir"

def test_join_two_paths_when_second_is_not_rooted():
    fs = FileSystem()
    assert fs.join("/fake", "dir") == "/fake/dir"

def test_join_two_paths_when_second_is_virtual():
    fs = FileSystem()
    assert fs.join("/fake", "../dir") == "/fake/../dir"

def test_join_returns_empty_string_when_empty():
    fs = FileSystem()
    assert fs.join('') == ''

def test_join_returns_empty_string_when_null():
    fs = FileSystem()
    assert fs.join() == ''

def test_join_returns_rooted_path_when_second_path_is_empty():
    fs = FileSystem()
    assert fs.join("/root","") == '/root/'

def test_dirname_returns_last_dir():
    fs = FileSystem()
    assert fs.dirname("/root/test/index.html") == '/root/test'

