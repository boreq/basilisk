from basilisk import helpers


def test_replace_ext():
    assert helpers.replace_ext('dir1/dir2/file.ext1', '.ext1', '.ext2') == \
                               'dir1/dir2/file.ext2'
