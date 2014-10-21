
Ark
===

Ark is a static website generator in Python 3. It transforms a directory of text files written in [Syntex][] or [Markdown][] into a self-contained website that can be viewed locally or served remotely.

[Syntex]: https://github.com/dmulholland/syntex
[Markdown]: http://daringfireball.net/projects/markdown/

Initialize a new site:

    $ ark init <site-name>

Build a site:

    $ ark build

Ark is under active development and is not yet ready for production use.


Installation
------------

Install directly from the Python Package Index using `pip`:

    $ pip install ark

Ark requires Python 3.2 or later.


Dependencies
------------

The following dependencies are installed automatically by `pip`:

* [Click][]
* [Ibis][]
* [Markdown][MD]
* [Pygments][]
* [PyYAML][]
* [Syntex][]

[MD]: https://pythonhosted.org/Markdown/
[PyYAML]: http://pyyaml.org/
[Pygments]: http://pygments.org/
[Syntex]: http://github.com/dmulholland/syntex
[Ibis]: http://github.com/dmulholland/ibis
[Click]: http://click.pocoo.org/


License
-------

This work has been placed in the public domain.
