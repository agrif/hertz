import os.path
import shlex
import os
from .command import ProjectCommand, recurse

class Map(ProjectCommand):
    help = 'run quartus_map'

    def run(self, proj, args):
        proj.call(['quartus_map', proj.qpf])

class Fit(ProjectCommand):
    help = 'run quartus_fit'

    def run(self, proj, args):
        proj.call(['quartus_fit', proj.qpf])

class Asm(ProjectCommand):
    help = 'run quartus_asm'

    def run(self, proj, args):
        proj.call(['quartus_asm', proj.qpf])

class Qsys(ProjectCommand):
    help = 'run qsys-generate'

    parser.add_argument('qsys', help='the qsys file to generate')
    parser.add_argument('--language', help='the language to generate', choices=['verilog', 'vhdl'], default='verilog')
    parser.add_argument('--output', help='the output directory', default=None)

    def run(self, proj, args):
        output = args.output
        if not output:
            output = os.path.splitext(args.qsys)[0]
        proj.call(['qsys-generate', args.qsys, '--synthesis=' + args.language.upper(), '--output-directory=' + output])
        with open(os.path.join(output, '.gitignore'), 'w') as f:
            f.write('*')

class Nios2(ProjectCommand):
    help = 'generate a nios2 makefile'

    parser.add_argument('sopc', help='the sopcinfo file to use')
    parser.add_argument('output', help='directory containing sources to build')
    parser.add_argument('--bsp', help='bsp type (ignored when updating)', default='hal')

    def run(self, proj, args):
        bspdir = os.path.join(args.output, 'bsp')
        basename = os.path.basename(args.output)

        if not os.path.isdir(args.output):
            os.makedirs(args.output)
            with open(os.path.join(args.output, 'main.c'), 'w') as f:
                f.write('#include <stdio.h>\n')
                f.write('\n')
                f.write('int main() {\n')
                f.write('    printf("Hello, world!");\n')
                f.write('    return 0;\n')
                f.write('}\n')
            with open(os.path.join(args.output, '.gitignore'), 'w') as f:
                f.write('/bsp/\n')
                f.write('/obj/\n')
                f.write('/Makefile\n')
                f.write('/' + basename + '.elf\n')
                f.write('/' + basename + '.map\n')
                f.write('/' + basename + '.objdump\n')
        
        proj.call(['nios2-bsp', args.bsp, bspdir, args.sopc])
        proj.call(['nios2-app-generate-makefile', '--bsp-dir', bspdir, '--app-dir', args.output, '--elf-name', basename + '.elf', '--src-dir', args.output])

class Build(ProjectCommand):
    help = 'run the build sequence configured in .hertz'

    def run(self, proj, args):
        os.chdir(proj.path)
        sequence = self.conf.get('commands', [])
        for cmd in sequence:
            cmd = shlex.split(str(cmd))
            if cmd[0] == 'hz':
                recurse(*cmd[1:])
            else:
                proj.call(cmd)
