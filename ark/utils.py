# --------------------------------------------------------------------------
# Utility functions.
# --------------------------------------------------------------------------

import collections
import os
import unicodedata
import re
import shutil
import datetime

import yaml


# Named tuples for file and directory information.
DirInfo = collections.namedtuple('DirInfo', 'path, name')
FileInfo = collections.namedtuple('FileInfo', 'path, name, base, ext')


# Returns a list of subdirectories of the specified directory.
def subdirs(directory):
    directories = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path):
            directories.append(DirInfo(path, name))
    return directories


# Returns a list of files in the specified directory.
def files(directory):
    files = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            files.append(fileinfo(path))
    return files


# Returns a FileInfo instance for the specified filepath.
def fileinfo(path):
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    return FileInfo(path, name, base, ext.strip('.'))


# Returns a list of source files in the specified directory.
def srcfiles(directory):
    extensions = ('txt', 'stx', 'md', 'html')
    return [fi for fi in files(directory) if fi.ext in extensions]


# Returns the creation time of the specified file.
# This function works on OSX, BSD, and Windows. On Linux it returns the
# time of the file's last metadata change.
def get_creation_time(path):
    stat = os.stat(path)
    if hasattr(stat, 'st_birthtime') and stat.st_birthtime:
        return datetime.datetime.fromtimestamp(stat.st_birthtime)
    else:
        return datetime.datetime.fromtimestamp(stat.st_ctime)


# Slug preparation function. Used to sanitize url components, etc.
def slugify(s):
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = s.replace("'", '')
    s = re.sub(r'[^a-z0-9-]+', '-', s)
    s = re.sub(r'--+', '-', s)
    return s.strip('-')


# Returns a titlecased version of the supplied string.
def titlecase(s):
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda m: m.group(0)[0].upper() + m.group(0)[1:],
        s
    )


# Copies the contents of srcdir to dstdir.
#
#   * Creates the destination directory if necessary.
#   * If noclobber is true, will never overwrite existing files.
#   * If onlyolder is true, will only overwrite older files.
#
def copydir(srcdir, dstdir, skiptypes=True, noclobber=False, onlyolder=True):

    if not os.path.exists(srcdir):
        return

    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    for name in os.listdir(srcdir):
        src = os.path.join(srcdir, name)
        dst = os.path.join(dstdir, name)

        if skiptypes and name.startswith('['):
            continue

        if name in ('__pycache__', '.DS_Store'):
            continue

        if os.path.isfile(src):
            copyfile(src, dst, noclobber, onlyolder)

        elif os.path.isdir(src):
            copydir(src, dst, False, noclobber, onlyolder)


# Copies the file src as dst.
#
#   * If noclobber is true, will never overwrite an existing dst.
#   * If onlyolder is true, will only overwrite dst if dst is older.
#
def copyfile(src, dst, noclobber=False, onlyolder=True):

    if os.path.isfile(dst):
        if noclobber:
            return
        if onlyolder and os.path.getmtime(src) <= os.path.getmtime(dst):
            return

    shutil.copy2(src, dst)


# Clears the contents of a directory.
def cleardir(dirpath):
    if os.path.isdir(dirpath):
        for name in os.listdir(dirpath):
            path = os.path.join(dirpath, name)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


# Writes a string to a file. Creates parent directories if required.
def writefile(path, content):
    path = os.path.abspath(path)

    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


# Creates a redirect page at the specified filepath.
def make_redirect(filepath, url):
    html = """\
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="refresh" content="0; url=%s">
    </head>
    <body></body>
</html>
""" % url
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(html)


# Loads a source file and parses its yaml header if present.
def load(filepath):
    with open(filepath, encoding='utf-8') as file:
        text, meta = file.read(), {}

    match = re.match(r"^---\n(.*?\n)[-.]{3}\n+", text, re.DOTALL)
    if match:
        text = text[match.end(0):]
        data = yaml.load(match.group(1))
        if isinstance(data, dict):
            for key, value in data.items():
                meta[key.lower().replace(' ', '_').replace('-', '_')] = value

    return text, meta


# Upgrade a site initialized by an older version of Ark
# that used a .ark directory in place of a .ark file.
# This function is temporary and will be removed.
def upgrade_dotark_dir(path):
    shutil.rmtree(os.path.join(path, '.ark'))
    writefile(os.path.join(path, '.ark'), '')
