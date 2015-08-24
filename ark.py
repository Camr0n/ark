#!/usr/bin/env python3
"""
Ark: a static website generator in Python 3.

Ark transforms a directory of text files written in Syntex or Markdown
into a static website that can be viewed locally or served remotely.

This script functions as the application's entry point. It is only
used during development as installing Ark via pip automatically generates
a new entry point on the user's PATH.

Author: Darren Mulholland <dmulholland@outlook.ie>
License: Public Domain

"""

import ark

# The cli module contains Ark's command line interface.
ark.cli.cli()
