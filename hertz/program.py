from .command import ProjectCommand

class Program(ProjectCommand):
    help = 'run quartus_pgm'

    parser.add_argument('program', help='the program file to load', default=None, nargs='?')
    parser.add_argument('--cable', help='the cable to use', default='USB-Blaster')
    parser.add_argument('--mode', help='the programming mode to use', default='JTAG')

    def run(self, proj, args):
        program = args.program
        if not program:
            program = proj.file(proj.name + '.sof')
        proj.call(['quartus_pgm', '-c', args.cable, '-m', args.mode, '-o', 'P;' + program])
