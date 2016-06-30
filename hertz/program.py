import os.path
from .command import ProjectCommand

class Program(ProjectCommand):
    help = 'run quartus_pgm'

    parser.add_argument('program', help='the program file to load', default=None, nargs='?')
    parser.add_argument('--cable', help='the cable to use', default='USB-Blaster')
    parser.add_argument('--mode', help='the programming mode to use', default='JTAG')

    def run(self, proj, args):
        program = args.program
        if not program:
            possibles = [proj.name + '.sof', proj.name + '_time_limited.sof']
            for p in possibles:
                program = proj.file(p)
                if os.path.isfile(program):
                    break
        if not program:
            raise RuntimeError('must specify program file to load')
        proj.call(['quartus_pgm', '-c', args.cable, '-m', args.mode, '-o', 'P;' + program])
