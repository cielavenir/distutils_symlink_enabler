### if your setup.py uses setuptools, import it before importing this module. ###

def copy_file(src, dst, preserve_mode=1, preserve_times=1, update=0,
              link=None, verbose=1, dry_run=0):
    """Copy a file 'src' to 'dst'.  If 'dst' is a directory, then 'src' is
    copied there with the same name; otherwise, it must be a filename.  (If
    the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode'
    is true (the default), the file's mode (type and permission bits, or
    whatever is analogous on the current platform) is copied.  If
    'preserve_times' is true (the default), the last-modified and
    last-access times are copied as well.  If 'update' is true, 'src' will
    only be copied if 'dst' does not exist, or if 'dst' does exist but is
    older than 'src'.

    'link' allows you to make hard links (os.link) or symbolic links
    (os.symlink) instead of copying: set it to "hard" or "sym"; if it is
    None (the default), files are copied.  Don't set 'link' on systems that
    don't support it: 'copy_file()' doesn't check if hard or symbolic
    linking is available. If hardlink fails, falls back to
    _copy_file_contents().

    Under Mac OS, uses the native file copy function in macostools; on
    other systems, uses '_copy_file_contents()' to copy file contents.

    Return a tuple (dest_name, copied): 'dest_name' is the actual name of
    the output file, and 'copied' is true if the file was copied (or would
    have been copied, if 'dry_run' true).
    """
    # XXX if the destination file already exists, we clobber it if
    # copying, but blow up if linking.  Hmmm.  And I don't know what
    # macostools.copyfile() does.  Should definitely be consistent, and
    # should probably blow up if destination exists and we would be
    # changing it (ie. it's not already a hard/soft link to src OR
    # (not update) and (src newer than dst).

    import os
    from distutils.file_util import _copy_file_contents, _copy_action
    from distutils import log

    from distutils.dep_util import newer
    from stat import ST_ATIME, ST_MTIME, ST_MODE, S_IMODE

    if os.path.islink(src):
        if os.path.exists(dst):
            os.unlink(dst)
        os.symlink(os.readlink(src), dst)
        return (dst, 1)

    if not os.path.isfile(src):
        raise DistutilsFileError(
              "can't copy '%s': doesn't exist or not a regular file" % src)

    if os.path.isdir(dst):
        dir = dst
        dst = os.path.join(dst, os.path.basename(src))
    else:
        dir = os.path.dirname(dst)

    if update and not newer(src, dst):
        if verbose >= 1:
            log.debug("not copying %s (output up-to-date)", src)
        return (dst, 0)

    try:
        action = _copy_action[link]
    except KeyError:
        raise ValueError("invalid value '%s' for 'link' argument" % link)

    if verbose >= 1:
        if os.path.basename(dst) == os.path.basename(src):
            log.info("%s %s -> %s", action, src, dir)
        else:
            log.info("%s %s -> %s", action, src, dst)

    if dry_run:
        return (dst, 1)

    # If linking (hard or symbolic), use the appropriate system call
    # (Unix only, of course, but that's the caller's responsibility)
    elif link == 'hard':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            try:
                os.link(src, dst)
                return (dst, 1)
            except OSError:
                # If hard linking fails, fall back on copying file
                # (some special filesystems don't support hard linking
                #  even under Unix, see issue #8876).
                pass
    elif link == 'sym':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            os.symlink(src, dst)
            return (dst, 1)

    # Otherwise (non-Mac, not linking), copy the file contents and
    # (optionally) copy the times and mode.
    _copy_file_contents(src, dst)
    if preserve_mode or preserve_times:
        st = os.stat(src)

        # According to David Ascher <da@ski.org>, utime() should be done
        # before chmod() (at least under NT).
        if preserve_times:
            os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
        if preserve_mode:
            os.chmod(dst, S_IMODE(st[ST_MODE]))

    return (dst, 1)

def copy_tree(src, dst, preserve_mode=1, preserve_times=1,
              preserve_symlinks=0, update=0, verbose=1, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.  The
    return value is unaffected by 'update' or 'dry_run': it is simply
    the list of all files under 'src', with the names changed to be
    under 'dst'.

    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be
    copied as symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' and 'verbose' are the same as for 'copy_file'.
    """
    preserve_symlinks = 1
    import os
    from distutils.dir_util import mkpath
    from distutils import log

    from distutils.file_util import copy_file

    if not dry_run and not os.path.isdir(src):
        raise DistutilsFileError(
              "cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except OSError as e:
        if dry_run:
            names = []
        else:
            raise DistutilsFileError(
                  "error listing files in '%s': %s" % (src, e.strerror))

    if not dry_run:
        mkpath(dst, verbose=verbose)

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if n.startswith('.nfs'):
            # skip NFS rename files
            continue

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if verbose >= 1:
                log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                if os.path.exists(dst_name):
                    os.unlink(dst_name)
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose, dry_run=dry_run))
        else:
            copy_file(src_name, dst_name, preserve_mode,
                      preserve_times, update, verbose=verbose,
                      dry_run=dry_run)
            outputs.append(dst_name)

    return outputs

if True:  # fake indent
    def make_release_tree(self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        import os
        from distutils import dir_util
        from distutils import log

        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        if hasattr(os, 'link'):        # can make hard links on this system
            link = 'hard'
            msg = "making hard links in %s..." % base_dir
        else:                           # nope, have to copy
            link = None
            msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file) and not os.path.islink(file):
                log.warn("'%s' not a regular file -- skipping", file)
            else:
                dest = os.path.join(base_dir, file)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

if True:  # fake indent
    def find_data_files_distutils(self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        from glob import glob
        import os
        from distutils.util import convert_path

        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))
        files = []
        for pattern in globs:
            # Each pattern has to be converted to a platform-specific path
            filelist = glob(os.path.join(src_dir, convert_path(pattern)))
            # Files that match more than one pattern are only added once
            files.extend([fn for fn in filelist if fn not in files
                and (os.path.isfile(fn) or os.path.islink(fn))])
        return files

if True:  # fake indent
    def find_data_files_setuptools(self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        from glob import glob
        import itertools
        import os

        patterns = self._get_platform_patterns(
            self.package_data,
            package,
            src_dir,
        )
        globs_expanded = map(glob, patterns)
        # flatten the expanded globs into an iterable of matches
        globs_matches = itertools.chain.from_iterable(globs_expanded)
        glob_files = [e for e in globs_matches if os.path.isfile(e) or os.path.islink(e)]
        files = itertools.chain(
            self.manifest_files.get(package, []),
            glob_files,
        )
        return self.exclude_data_files(package, src_dir, files)

from distutils import dir_util
dir_util.copy_tree = copy_tree

from distutils import file_util
file_util.copy_file = copy_file

from distutils.command import sdist
sdist.sdist.make_release_tree = make_release_tree

from distutils.command import build_py as build_py_distutils
build_py_distutils.build_py.find_data_files = find_data_files_distutils

import sys
if __name__ == '__main__' or 'setuptools' in sys.modules:
    from setuptools.command import build_py as build_py_setuptools
    build_py_setuptools.build_py.find_data_files = find_data_files_setuptools

if __name__ == '__main__':
    # pretty not sure what should be main, but how about pip with distutils patched?
    from pip import __main__
    sys.exit(__main__._main())
