import yaml
import os
import os.path
import sys

def find_settings(path=None):
    if path is None:
        path = os.curdir
    path = os.path.abspath(path)

    homepath = os.path.expanduser('~/.hertz')
    homepath = os.path.abspath(path)
    settings = {}
    if os.path.isfile(homepath):
        with open(homepath) as fp:
            try:
                settings.update(yaml.safe_load(fp))
            except Exception:
                raise RuntimeError('invalid config file: ' + homepath) from None

    while path:
        f = os.path.join(path, '.hertz')
        if f == homepath:
            # don't go further, this is the main file I guess
            return settings
        if os.path.isfile(f):
            with open(f) as fp:
                try:
                    settings.update(yaml.safe_load(fp))
                except Exception:
                    raise RuntimeError('invalid config file: ' + f) from None
            return settings
        newpath = os.path.dirname(path)[0]
        if newpath == path:
            # we hit root
            return settings
        path = newpath

    return settings
