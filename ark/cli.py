
""" Command line interface. """

import os
import sys
import shutil
import datetime
import subprocess
import http.server
import webbrowser

import clio

from . import meta
from . import main
from . import utils


# Application help text.
apphelp = """
Usage: %s [FLAGS] [COMMAND]

  Static website generator.

Flags:
  --help            Print the application's help text and exit.
  --version         Print the application's version number and exit.

Commands:
  build             Build the current site.
  clear             Clear the output directory.
  init              Initialize a new site directory.
  new               Create a new record file.
  serve             Run a web server on the site's output directory.

Command Help:
  help <command>    Print the specified command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the build command.
buildhelp = """
Usage: %s build [FLAGS] [OPTIONS]

  Build the current site. This command can be run from the site directory
  or any of its subdirectories.

Flags:
  --clear           Clear the output directory before building.
  --help            Print the build command's help text and exit.

Options:
  --out <path>      Redirect output to the specified directory.
  --theme <name>    Override the theme specififed in the config file.

""" % os.path.basename(sys.argv[0])


# Help text for the init command.
inithelp = """
Usage: %s init [FLAGS] [ARGUMENTS]

  Initialize a new site directory. If a directory path is specified,
  that directory will be created and used. Otherwise, the current
  directory will be used.

Arguments:
  [dirname]         Directory name. Defaults to the current directory.

Flags:
  --help            Print the init command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the clear command.
clearhelp = """
Usage: %s clear [FLAGS]

  Clear the output directory.

Flags:
  --help            Print the clear command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the new command.
newhelp = """
Usage: %s new [FLAGS] ARGUMENTS

  Create a new record file.

Arguments:
  <type>            Record type, e.g. 'posts'.
  <name>            Record filename.

Flags:
  --help            Print the new command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text for the serve command.
servehelp = """
Usage: %s serve [FLAGS] [OPTIONS]

  Serve the site's output directory using Python's builtin web server.

Options:
  -h, --host <str>  Host IP address. Defaults to localhost.
  -p, --port <int>  Port number. Defaults to 8080.

Flags:
  --help            Print the serve command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Attempt to locate the site's home directory.
def locate_home_directory():
    path = os.getcwd()
    while True:
        if os.path.exists(os.path.join(path, 'src')):
            return os.path.abspath(path)
        path = os.path.join(path, '..')
        if not os.path.isdir(path):
            break
    sys.exit('Error: cannot locate site directory.')


# Application entry point.
def cli():
    parser = clio.ArgParser(apphelp, meta.__version__)

    build_parser = parser.add_command("build", build, buildhelp)
    build_parser.add_flag("clear")
    build_parser.add_str_option("out", None)
    build_parser.add_str_option("theme", None)

    init_parser = parser.add_command("init", init, inithelp)
    clear_parser = parser.add_command("clear", clear, clearhelp)
    new_parser = parser.add_command("new", new, newhelp)

    serve_parser = parser.add_command("serve", serve, servehelp)
    serve_parser.add_str_option("host", "localhost", "h")
    serve_parser.add_int_option("port", 8080, "p")

    parser.parse()
    if not parser.has_cmd():
      parser.help()


# Callback for the build command.
def build(parser):
    parser['home'] = locate_home_directory()
    main.build(parser.get_options())


# Callback for the init command.
def init(parser):
    dirpath = parser.get_args()[0] if parser.has_args() else '.'
    os.makedirs(dirpath, exist_ok=True)
    os.chdir(dirpath)
    for dirname in ('.ark', 'ext', 'inc', 'lib', 'out', 'src'):
        os.makedirs(dirname, exist_ok=True)
    utils.copydir(os.path.join(os.path.dirname(__file__), 'init'), '.')


# Callback for the clear command.
def clear(parser):
  home = locate_home_directory()
  out = os.path.join(home, 'out')
  if os.path.exists(out):
      utils.cleardir(out)
  else:
      sys.exit("Error: cannot locate the out directory.")


# Callback for the new command.
def new(parser):
    args = parser.get_args()
    if len(args) != 2:
        sys.exit("Error: the 'new' command requires 2 arguments.")
    home = locate_home_directory()
    path = os.path.join(home, 'src', '[%s]' % args[0], args[1])
    if os.path.exists(path):
        sys.exit("Error: the file already exists.")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    template = "---\ndate: %s\n---\n\n\n"
    utils.writefile(path, template % now)
    editor = os.getenv('ARKEDITOR') or os.getenv('EDITOR') or 'vim'
    subprocess.call((editor, path))


# Callback for the serve command.
def serve(parser):
    home = locate_home_directory()
    root = os.path.join(home, 'out')

    if not os.path.exists(root):
        sys.exit("Error: cannot locate the out directory.")

    os.chdir(root)

    try:
        server = http.server.HTTPServer(
            (parser['host'], parser['port']),
            http.server.SimpleHTTPRequestHandler
        )
    except PermissionError:
        sys.exit("Permission error: use 'sudo' to run on a port number below 1024.")

    address = server.socket.getsockname()

    print("-" * 80)
    print("Root: %s" % root)
    print("Host: %s:%s"  % (address[0], address[1]))
    print("Stop: Ctrl-C")
    print("-" * 80)

    webbrowser.open("http://%s:%s" % (address[0], address[1]))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "-" * 80 + "Stopping server...\n" + "-" * 80);
        server.server_close()
