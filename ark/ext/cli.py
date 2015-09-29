# --------------------------------------------------------------------------
# This extension implements a pluggable command line interface for Ark.
#
# Author: Darren Mulholland <dmulholland@outlook.ie>
# License: Public Domain
# --------------------------------------------------------------------------

import os
import sys
import shutil
import datetime
import subprocess
import http.server
import webbrowser
import hashlib
import subprocess
import time

import clio
from ark import build, hooks, meta, site, utils


# Application help text.
apphelp = """
Usage: %s [FLAGS] [COMMAND]

  Static website generator.

Flags:
  --help              Print the application's help text and exit.
  --version           Print the application's version number and exit.

Commands:
  build               Build the site.
  clear               Clear the output directory.
  edit                Edit an existing record or create a new file.
  init                Initialize a new site directory.
  serve               Run a web server on the site's output directory.
  watch               Monitor the site directory and rebuild on changes.

Command Help:
  help <command>      Print the specified command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the build command.
buildhelp = """
Usage: %s build [FLAGS] [OPTIONS]

  Build the current site. This command can be run from the site directory
  or any of its subdirectories.

Flags:
  -c, --clear         Clear the output directory before building.
      --help          Print the build command's help text and exit.

Options:
  -i, --inc <path>    Override the default 'inc' directory.
  -l, --lib <path>    Override the default 'lib' directory.
  -o, --out <path>    Override the default 'out' directory.
  -s, --src <path>    Override the default 'src' directory.
  -t, --theme <name>  Override the theme specififed in the config file.

""" % os.path.basename(sys.argv[0])


# Help text for the init command.
inithelp = """
Usage: %s init [FLAGS] [ARGUMENTS]

  Initialize a new site directory. If a directory path is specified,
  that directory will be created and used. Otherwise, the current
  directory will be used. Existing files will not be overwritten.

Arguments:
  [dirname]           Directory name. Defaults to the current directory.

Flags:
  -e, --empty         Do not create a skeleton site.
      --help          Print the init command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the clear command.
clearhelp = """
Usage: %s clear [FLAGS]

  Clear the output directory.

Flags:
  --help              Print the clear command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the edit command.
edithelp = """
Usage: %s edit [FLAGS] ARGUMENTS

  Edit a record file or files. Creates new records if the named files
  do not exist.

Arguments:
  <type>              Record type, e.g. 'posts'.
  <name, ...>         Record filenames.

Flags:
  --help              Print the edit command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the serve command.
servehelp = """
Usage: %s serve [FLAGS] [OPTIONS]

  Serve the site's output directory using Python's builtin web server.

  Host IP defaults to localhost (127.0.0.1). Specify an IP address to serve
  only on that address or '0.0.0.0' to serve an all available IPs.

  Port number defaults to 8080 as ports below 1024 require sudo.
  Set to 0 to randomly select an available port.

Options:
  -h, --host <str>    Host IP address. Defaults to localhost.
  -p, --port <int>    Port number. Defaults to 8080.

Flags:
  -b, --browser       Launch the default web browser.
      --help          Print the serve command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the watch command.
watchhelp = """
Usage: %s watch [FLAGS]

  Monitor the site directory and automatically rebuild the site when any
  file changes are detected.

Flags:
  --help              Print the watch command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Initialize the command line interface on the 'init' hook.
@hooks.register('init')
def cli():
    parser = clio.ArgParser(apphelp, meta.__version__)

    build_parser = parser.add_command("build", cmd_build, buildhelp)
    build_parser.add_flag("clear", "c")
    build_parser.add_str_option("out", None, "o")
    build_parser.add_str_option("src", None, "s")
    build_parser.add_str_option("lib", None, "l")
    build_parser.add_str_option("inc", None, "i")
    build_parser.add_str_option("theme", None, "t")

    serve_parser = parser.add_command("serve", cmd_serve, servehelp)
    serve_parser.add_flag("browser", "b")
    serve_parser.add_str_option("host", "localhost", "h")
    serve_parser.add_int_option("port", 8080, "p")

    init_parser = parser.add_command("init", cmd_init, inithelp)
    init_parser.add_flag("empty", "e")

    clear_parser = parser.add_command("clear", cmd_clear, clearhelp)
    edit_parser = parser.add_command("edit", cmd_edit, edithelp)
    watch_parser = parser.add_command("watch", cmd_watch, watchhelp)

    hooks.event('clio', parser)

    parser.parse()
    if not parser.has_cmd():
      parser.help()


# Callback for the build command.
def cmd_build(parser):
    if site.homeless():
        sys.exit("Error: cannot locate the site's home directory.")

    if parser['out']: site.setconfig('[out]', parser['out'])
    if parser['src']: site.setconfig('[src]', parser['src'])
    if parser['lib']: site.setconfig('[lib]', parser['lib'])
    if parser['inc']: site.setconfig('[inc]', parser['inc'])

    if parser['theme']:
        site.setconfig('[theme]', site.locate_theme(parser['theme']))

    if parser['clear']:
        utils.cleardir(site.out())

    site.setconfig('[flags]', parser.get_args())

    @hooks.register('main')
    def build_callback():
        if os.path.isdir(site.src()):
            build.build_site()
        else:
            sys.exit("Error: cannot locate the site's source directory.")


# Callback for the init command.
def cmd_init(parser):
    initdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init')
    sitedir = parser.get_args()[0] if parser.has_args() else '.'
    os.makedirs(sitedir, exist_ok=True)
    os.chdir(sitedir)

    for name in ('ext', 'inc', 'lib', 'out', 'src'):
        os.makedirs(name, exist_ok=True)
    utils.writefile('.ark', '')

    if not os.path.exists('config.py'):
        shutil.copy2(os.path.join(initdir, 'config.py'), 'config.py')

    for name in ('ext', 'lib'):
        utils.copydir(os.path.join(initdir, name), name, noclobber=True)

    if not parser['empty']:
        for name in ('inc', 'src'):
            utils.copydir(os.path.join(initdir, name), name, False, True)


# Callback for the clear command.
def cmd_clear(parser):
    if site.homeless():
        sys.exit("Error: cannot locate the site's home directory.")

    if not os.path.exists(site.out()):
        sys.exit("Error: cannot locate the site's output directory.")

    utils.cleardir(site.out())


# Callback for the edit command.
def cmd_edit(parser):
    if site.homeless():
        sys.exit("Error: cannot locate the site's home directory.")

    args = parser.get_args()
    if len(args) < 2:
        sys.exit("Error: the 'edit' command requires at least 2 arguments.")

    paths = [site.src('[%s]' % args[0], path) for path in args[1:]]

    for path in paths:
        if not os.path.exists(path):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            template = "---\ntitle: Record Title\ndate: %s\n---\n\n\n"
            utils.writefile(path, template % now)

    paths.insert(0, os.getenv('ARK_EDITOR') or os.getenv('EDITOR') or 'vim')
    subprocess.call(paths)


# Callback for the serve command.
def cmd_serve(parser):
    if site.homeless():
        sys.exit("Error: cannot locate the site's home directory.")

    if not os.path.exists(site.out()):
        sys.exit("Error: cannot locate the site's output directory.")

    os.chdir(site.out())

    try:
        server = http.server.HTTPServer(
            (parser['host'], parser['port']),
            http.server.SimpleHTTPRequestHandler
        )
    except PermissionError:
        sys.exit("Permission error: use 'sudo' to run on a port number below 1024.")

    address = server.socket.getsockname()

    print("-" * 80)
    print("Root: %s" % site.out())
    print("Host: %s"  % address[0])
    print("Port: %s" % address[1])
    print("Stop: Ctrl-C")
    print("-" * 80)

    if parser['browser']:
        webbrowser.open("http://%s:%s" % (parser['host'], parser['port']))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "-" * 80 + "Stopping server...\n" + "-" * 80)
        server.server_close()


# Callback for the watch command. Python doesn't have a builtin file system
# watcher so we hack together one of our own.
def cmd_watch(parser):
    home = site.home()
    args = [sys.argv[0], 'build', 'watch'] + parser.get_args()

    print("-" * 80)
    print("Site: %s" % home)
    print("Stop: Ctrl-C")
    print("-" * 80)

    # Build the site at least once with the 'watch' flag.
    subprocess.call(args)

    # Create a hash digest of the site directory.
    oldhash = hashsite(home)

    try:
        while True:
            newhash = hashsite(home)
            if newhash != oldhash:
                subprocess.call(args)
                newhash = hashsite(home)
            oldhash = newhash
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    # Build the site one last time without the 'watch' flag.
    print("\n" + "-" * 80 + "Running final build...\n" + "-" * 80)
    subprocess.call(arg for arg in args if arg != 'watch')


# Returns a hash digest of the site directory.
def hashsite(sitedirpath):
    hash = hashlib.sha256()

    def hashdir(dirpath, is_home):
        for finfo in utils.files(dirpath):
            mtime = os.path.getmtime(finfo.path)
            hash.update(str(mtime).encode())
            hash.update(finfo.name.encode())

        for dinfo in utils.subdirs(dirpath):
            if is_home and dinfo.name in ('out'):
                continue
            hashdir(dinfo.path, False)

    hashdir(sitedirpath, True)
    return hash.digest()
