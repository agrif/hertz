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

class Build(ProjectCommand):
    help = 'run quartus_map, quartus_fit, quartus_asm'

    def run(self, proj, args):
        recurse('map')
        recurse('fit')
        recurse('asm')
