#!/usr/bin/env python3
# --------------------------------------------------------------------------
# Ark: a static website generator in Python 3.
#
# Ark transforms a directory of text files written in Syntex or Markdown
# into a static website that can be viewed locally or served remotely.
#
# This script acts as the application's entry point. It is only used during
# development as installing Ark via pip automatically generates a new entry
# point on the user's PATH.
#
# Author: Darren Mulholland <darren@mulholland.xyz>
# License: Public Domain
# --------------------------------------------------------------------------

import ark

# The main module contains the application's entry point.
ark.main.main()
