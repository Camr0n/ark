
# Ark

Ark is a static website generator written in Python. It transforms a
directory of text files into a self-contained website that can be viewed
locally or served remotely.

* Ark is extensible. It has builtin support for source files written
  in [Markdown][] and [Syntex][], but can be extended via plugins to support
  any similar text-to-html format.

* Ark is flexible. By default it produces sites with page-relative links
  that can be viewed locally without any need for a web server (ideal for
  distributing project documentation in html format), but it can easily
  produce sites with resource or directory-style urls.

See Ark's [documentation][] or the Ark [sample site][] for further details.

[Markdown]: http://daringfireball.net/projects/markdown/
[Syntex]: https://github.com/dmulholland/syntex
[documentation]: http://mulholland.xyz/docs/ark/
[sample site]: http://ark.mulholland.xyz



## Installation

Install directly from the Python Package Index using `pip`:

    $ pip install ark

Ark requires Python 3.2 or later.



## License

This work has been placed in the public domain.
