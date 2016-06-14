import argparse
import sys
import time
import shlex
from . import project, settings

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
        if add:
            p = subparsers.add_parser(classdict['name'], parents=[classdict['parser']], help=classdict['help'], aliases=classdict['aliases'])
            classdict['parser'] = p
        cls = super().__new__(self, name, bases, classdict)
        if add:
            subcommands[classdict['name']] = cls
        return cls

    def __init__(self, name, bases, classdict, add=True):
        super().__init__(name, bases, classdict)

class Command(metaclass=CommandMetaclass, add=False):
    def __init__(self, proj, args, conf):
        self.conf = conf
        self.args = args
        self.proj = proj
        self.run(proj, args)
    
    def run(self, proj, args):
        raise NotImplementedError(self.name)

    @classmethod
    def die(cls, s):
        print('hz {}:'.format(cls.name), s, file=sys.stderr)
        sys.exit(1)

class ProjectCommand(Command, add=False):
    def __init__(self, proj, args, conf):
        if not proj:
            raise RuntimeError('no project found')
        super().__init__(proj, args, conf)

def recurse(*argv):
    args = parser.parse_args(argv)

    proj = project.find_project()
    conf = settings.find_settings()

    Cmd = subcommands[args.subcommand]
    cmdconf = conf.get(args.subcommand, {})
    extra_argv = shlex.split(cmdconf.get('defaults', ''))
    extra_argv += list(argv)
    extra_argv.remove(args.subcommand)
    extra_argv.insert(0, args.subcommand)
    args = parser.parse_args(extra_argv)

    start = time.time()
    Cmd(proj, args, cmdconf)
    end = time.time()
    duration = end - start
    print('hz {} completed in {:.02f}s'.format(args.subcommand, duration))
