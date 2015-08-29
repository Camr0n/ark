
""" Utility functions. """

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


def subdirs(directory):
    """ Returns a list of subdirectories of the specified directory. """
    directories = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path):
            directories.append(DirInfo(path, name))
    return directories


def files(directory):
    """ Returns a list of files in the specified directory. """
    files = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            files.append(fileinfo(path))
    return files


def fileinfo(path):
    """ Returns a FileInfo instance for the specified filepath. """
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    return FileInfo(path, name, base, ext.strip('.'))


def srcfiles(directory):
    """ Returns a list of source files in the specified directory. """
    extensions = ('txt', 'stx', 'md', 'html')
    return [fi for fi in files(directory) if fi.ext in extensions]


def get_creation_time(path):
    """ Returns the creation time of the specified file.

    This function works on OSX, BSD, and Windows. On Linux it returns the
    time of the file's last metadata change.
    """
    stat = os.stat(path)
    if hasattr(stat, 'st_birthtime') and stat.st_birthtime:
        return datetime.datetime.fromtimestamp(stat.st_birthtime)
    else:
        return datetime.datetime.fromtimestamp(stat.st_ctime)


def slugify(s):
    """ Slug preparation function. Used to sanitize url components, etc. """
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = s.replace("'", '')
    s = re.sub(r'[^a-z0-9-]+', '-', s)
    s = re.sub(r'--+', '-', s)
    return s.strip('-')


def titlecase(s):
    """ Returns a titlecased version of the supplied string. """
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda m: m.group(0)[0].upper() + m.group(0)[1:],
        s
    )


def copydir(srcdir, dstdir, skip=True):
    """ Copies the contents of srcdir to dstdir.

    The destination directory is created if necessary. If a file with the same
    name exists in the destination directory, the source file is only copied
    if it has a newer modification timestamp. """

    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    for name in os.listdir(srcdir):
        src = os.path.join(srcdir, name)
        dst = os.path.join(dstdir, name)

        if skip and name.startswith('['):
            continue

        if name in ('__pycache__', '.DS_Store'):
            continue

        if os.path.isfile(src):
            if os.path.isfile(dst):
                if os.path.getmtime(src) <= os.path.getmtime(dst):
                    continue
            shutil.copy2(src, dst)

        elif os.path.isdir(src):
            copydir(src, dst, False)


def cleardir(dirpath):
    """ Clears the contents of a directory. """
    if os.path.isdir(dirpath):
        for name in os.listdir(dirpath):
            path = os.path.join(dirpath, name)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)


def writefile(filepath, content):
    """ Writes a string to a file. Creates directories if required. """
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)


def make_redirect(filepath, url):
    """ Creates a redirect page at the specified filepath. """
    html = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Redirect</title>
        <meta http-equiv="refresh" content="0; url=%s">
    </head>
    <body></body>
</html>
""" % url
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(html)


def load(filepath):
    """ Loads a source file and parses its yaml header if present. """

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
