import argparse
import sys

parser = argparse.ArgumentParser(prog='hz')
subparsers = parser.add_subparsers(metavar='COMMAND', dest='subcommand')
subparsers.required = True

def camel_to_command(s):
    pos = [i for i,e in enumerate(s+'A') if e.isupper()]
    parts = [s[pos[j]:pos[j+1]] for j in range(len(pos)-1)]
    return '-'.join(p.lower() for p in parts)

subcommands = {}

class CommandMetaclass(type):
    @classmethod
    def __prepare__(cls, name, bases, add=True):
        parents = []
        for base in bases:
            if not issubclass(base, Command):
                continue
            parents.append(base.parser)
        p = argparse.ArgumentParser(add_help=False, parents=parents)
        return dict(parser=p, name=camel_to_command(name), help='', aliases=[])

    def __new__(self, name, bases, classdict, add=True):
        global subcommands
        cls = super().__new__(self, name, bases, classdict)
        if add:
            subparsers.add_parser(classdict['name'], parents=[classdict['parser']], help=classdict['help'], aliases=classdict['aliases'])
            subcommands[classdict['name']] = cls
        return cls

    def __init__(self, name, bases, classdict, add=True):
        super().__init__(name, bases, classdict)

class Command(metaclass=CommandMetaclass, add=False):
    def run(self, args):
        raise NotImplementedError(self.name)

    @classmethod
    def die(cls, s):
        print('hz {}:'.format(cls.name), s, file=sys.stderr)
        sys.exit(1)
