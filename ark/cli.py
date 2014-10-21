
""" Command line interface. """

import os
import sys
import shutil

import click

from . import meta
from . import main
from . import utils


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version %s' % meta.__version__)
    ctx.exit()


def locate_home_directory():
    path = os.getcwd()
    while True:
        if os.path.exists(os.path.join(path, 'src')):
            return path
        path = os.path.join(path, '..')
        if not os.path.isdir(path):
            break
    sys.exit('Error: cannot locate site directory.')


@click.group()
@click.option('--version', is_flag=True, expose_value=False, is_eager=True,
    callback=print_version,
    help='Print version number and exit.')
def cli():
    """ Static website generator. """
    pass


@cli.command()
@click.option('--theme', metavar='<name>',
    help='Override the theme specififed in the config file.')
@click.option('--out', metavar='<path>',
    help='Redirect output to this directory.')
@click.option('--clear', is_flag=True, default=False,
    help='Clear the output directory before building.')
def build(theme, out, clear, ):
    """ Build site. """
    options = {
        'home': locate_home_directory()
    }

    if theme:
        options['theme'] = theme

    if out:
        options['out'] = out

    if clear:
        options['clear'] = True

    main.build(options)


@cli.command()
@click.argument('name')
def init(name):
    """ Create new site. """
    if os.path.exists(name):
        sys.exit('Error: "%s" already exists.' % os.path.abspath(name))

    os.makedirs(name)
    os.makedirs(os.path.join(name, 'ext'))
    os.makedirs(os.path.join(name, 'inc'))
    os.makedirs(os.path.join(name, 'lib'))
    os.makedirs(os.path.join(name, 'out'))
    os.makedirs(os.path.join(name, 'src'))

    utils.copydir(
        os.path.join(os.path.dirname(__file__), 'skeleton'),
        name
    )

    utils.copydir(
        os.path.join(os.path.dirname(__file__), 'themes', 'vanilla'),
        os.path.join(name, 'lib', 'vanilla')
    )
