
""" Command line interface. """

import os
import sys
import shutil

from . import clio
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
  init              Initialize a new site directory.

Command Help:
  help <command>    Print the specified command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Help text forthe build command.
buildhelp = """
Usage: %s build [FLAGS] [OPTIONS]

  Build the current site.

Flags:
  --clear           Clear the output directory before building.
  --help            Print the build command's help text and exit.

Options:
  --out <path>      Redirect output to the specified directory.
  --theme <name>    Override the theme specififed in the config file.

""" % os.path.basename(sys.argv[0])


# Help text for the init command.
inithelp = """
Usage: %s init [FLAGS]

  Initialize a new site directory.

Flags:
  --help            Print the init command's help text and exit.

""" % os.path.basename(sys.argv[0])


# Application entry point.
def cli():
    parser = clio.ArgParser(apphelp, meta.__version__)

    build_parser = parser.add_command("build", build, buildhelp)
    build_parser.add_flag("clear")
    build_parser.add_str_option("out", None)
    build_parser.add_str_option("theme", None)

    init_parser = parser.add_command("init", init, inithelp)

    args = parser.parse()
    if not args.has_cmd():
      parser.help()


# Callback for the build command.
def build(argset):
    options = argset.get_options()
    options['home'] = locate_home_directory()
    main.build(options)


# Callback for the init command.
def init(argset):
    for name in ('.ark', 'ext', 'inc', 'lib', 'out', 'src'):
        if not os.path.exists(name):
            os.makedirs(name)
    utils.copydir(os.path.join(os.path.dirname(__file__), 'init'), '.')


# Attempt to locate the site's home directory.
def locate_home_directory():
    path = os.getcwd()
    while True:
        if os.path.exists(os.path.join(path, 'src')):
            return path
        path = os.path.join(path, '..')
        if not os.path.isdir(path):
            break
    sys.exit('Error: cannot locate site directory.')
