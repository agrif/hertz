import os
import os.path
import shutil
import time
from .command import Command
from .project import Project

skeletons = {}

def skel_basic(name, family, device, base=None, exts=['.qsf', '.sdc']):
    global skeletons
    if base is None:
        base = name
    skel = {
        'name': name,
        'family': family,
        'device': device,
        'files': [name + ext for ext in exts]
    }
    skeletons[name] = skel

skel_basic('de2-115', 'Cyclone IV E', 'EP4CE115F29C7')

def entityfy(s):
    return s.lower().replace('-', '_')

class ListSkeletons(Command):
    help = 'list the available project skeletons'

    def run(self, args):
        skels = sorted(skeletons.keys())
        for skel in skels:
            d = skeletons[skel]
            print('{} ({} {})'.format(skel, d['family'], d['device']))

class Init(Command):
    help = 'write out a Quartus project skeleton'

    parser.add_argument('output', help='directory to write output to')
    parser.add_argument('skeleton', help='the skeleton to use (list-skeletons for a list)')
    parser.add_argument('--name', help='project name', default=None)
    parser.add_argument('--toplevel', help='toplevel entity', default=None)
    parser.add_argument('-f', '--force', action='store_true', default=False, help='create skeleton even if not empty')

    def run(self, args):
        # make sure we can read skeleton data
        self.skelpath = os.path.join(os.path.dirname(__file__), 'skeletons')
        if not os.path.isfile(os.path.join(self.skelpath, 'gitignore')):
            self.die('cannot find skeleton data')

        # start the template data
        self.data = {}

        # figure out output path and project name
        self.outpath = os.path.abspath(args.output)
        self.name = args.name
        if not self.name:
            self.name = os.path.basename(self.outpath)
        self.data['project_name'] = self.name

        # figure out the toplevel entity
        self.toplevel = args.toplevel
        if not self.toplevel:
            self.toplevel = entityfy(self.name)
        self.data['toplevel_entity'] = self.toplevel

        # make sure the skeleton is valid
        if not args.skeleton in skeletons:
            self.die('invalid skeleton: {} (use list-skeletons to see valid skeletons)'.format(args.skeleton))
        self.skel = skeletons[args.skeleton]
        self.data['skeleton_name'] = self.skel['name']
        self.data['family'] = self.skel['family']
        self.data['device'] = self.skel['device']

        # see if the directory is empty
        if os.path.isdir(self.outpath) and os.listdir(self.outpath) != []:
            if not args.force:
                self.die('directory not empty: use -f to force')

        # make sure the directory exists
        if not os.path.isdir(self.outpath):
            os.makedirs(self.outpath)

        # create a quartus-formatted date
        self.data['quartus_date'] = time.strftime('%H:%M:%S %B %d, %Y')

        # copy in some files
        self.copy_in('gitignore', '.gitignore')
        self.copy_in('default.qpf')
        verilog = self.copy_in('default.v')
        for fname in self.skel['files']:
            self.copy_in(fname)

        proj = Project(self.outpath)
        proj.add_source(verilog)

    def copy_in(self, src, dest=None, interpolate=True):
        fullsrc = os.path.join(self.skelpath, src)
        if not dest:
            ext = os.path.splitext(fullsrc)[1]
            dest = self.name + ext
        fulldest = os.path.join(self.outpath, dest)
        
        if not interpolate:
            shutil.copyfile(fullsrc, fulldest)
            return

        with open(fullsrc) as fs:
            with open(fulldest, 'w') as fd:
                fd.write(fs.read().format(**self.data))
        return fulldest
