from .command import ProjectCommand

class Add(ProjectCommand):
    help = 'add a source file to the project'

    parser.add_argument('source', help='the source file to add')

    def run(self, proj, args):
        proj.add_source(args.source)

class Rm(ProjectCommand):
    help = 'remove a source file from the project'

    parser.add_argument('source', help='the source file to remove')

    def run(self, proj, args):
        proj.rm_source(args.source)
