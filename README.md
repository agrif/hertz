hertz
-----

This is a basic command line tool in the style of git, to make dealing
with Quartus command line tools a bit more palatable.

Quickstart:

    alias hz='python3 -m hertz.main'
    hz init new-project/ de2-115
    cd new-project/
    hz build

*hertz* will read a `.hertz` file (YAML) as configuration, so take a
peek in there.

Work in progress.
