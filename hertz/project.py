import subprocess
import contextlib
import os.path
import errno
import pty # sorry windows
import select
import re
import os

class QuartusPopen(subprocess.Popen):
    ansi_re = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    type_re = re.compile(r'^([A-Z][a-z]*)(?: \(([0-9]+)\))?: (.*)$', re.DOTALL)
    def __init__(self, args, **kwargs):
        ours, theirs = pty.openpty()
        kwargs = kwargs.copy()
        kwargs['stdout'] = theirs
        kwargs['stdin'] = theirs
        kwargs['stderr'] = subprocess.STDOUT
        kwargs['close_fds'] = True
        kwargs['bufsize'] = 1
        super().__init__(args, **kwargs)
        os.close(theirs)
        self.pty = os.fdopen(ours)

    def readlines(self):
        # we have to be careful, self.pty will sometimes hang if you try to
        # read it after the process dies. So we use select, to be sure we
        # *can* read it, and os.read, to allow reading less than all bytes
        #
        # we have to use pty because glibc (bless 'em) always opens pipes
        # in buffered mode, but we want unbuffered, interactive output
        #
        # finally, remember to call self.poll() or self.wait() to
        # remove defunct processes.
        #
        # (The official Quartus IDE has some trouble with this on Linux,
        # it tends to hang at 97% for a *long* time, and leaves the
        # defunct.)
        poll = select.poll()
        poll.register(self.pty, select.POLLIN)
        buf = b''
        
        while True:
            for fd, cond in poll.poll(0.1):
                if not cond & select.POLLIN:
                    pass
                try:
                    # we can read
                    buf += os.read(self.pty.fileno(), 512)
                except IOError as e:
                    if e.errno == errno.EIO:
                        # EIO can mean EOF, here
                        pass
                    else:
                        raise

            # is the process done? have we read everything?
            if self.poll() != None and not buf:
                # it is done! finish up here
                self.wait()
                return

            while b'\n' in buf or (buf and self.poll() != None):
                # we found a whole line
                line, *rest = buf.splitlines(True)
                buf = b''.join(rest)
                line = line.decode(errors='replace')
            
                line = self.ansi_re.sub('', line)
                line = line.strip()
                g = self.type_re.match(line)
                if g:
                    typ, num, text = g.groups()
                    typ = typ.lower()
                    if num:
                        num = int(num)
                else:
                    typ = None
                    num = None
                    text = line
                yield (typ, num, text)

    def display(self):
        for typ, num, text in self.readlines():
            #if typ == 'info':
            #    continue
            if typ and num:
                print (typ + '(' + str(num) + '):', text)
            if typ:
                print(typ + ':', text)
            else:
                print(text)

def find_project(path=None):
    if path is None:
        path = os.curdir
    path = os.path.abspath(path)
    while path:
        for fname in os.listdir(path):
            if fname.endswith('.qpf'):
                return Project(path)
        newpath = os.path.dirname(path)
        if path == newpath:
            # we hit root
            return None
        path = newpath

class Project:
    def __init__(self, path):
        self.path = path
        self.reload()

    def reload(self):
        if not os.path.isdir(self.path):
            raise RuntimeError('quartus project is not a directory')

        self.qpf = self.find_file('qpf')
        self.qsf = self.find_file('qsf')
        self.name, _ = os.path.splitext(self.qpf)

    def file(self, path):
        return os.path.join(self.path, path)

    def find_file(self, ext):
        fext = '.' + ext
        for fname in os.listdir(self.path):
            if fname.endswith(fext):
                return self.file(fname)
        else:
            raise RuntimeError('could not find {} file'.format(ext.upper()))

    def call(self, args, **kwargs):
        proc = QuartusPopen(args, **kwargs)
        proc.display()
        if proc.returncode:
            cmd = kwargs.get('args')
            if cmd is None:
                cmd = args[0]
            raise subprocess.CalledProcessError(proc.returncode, cmd)

    @contextlib.contextmanager
    def settings(self):
        def uncomment(s):
            if '#' in s:
                s, _ = s.split('#', 1)
            return s.strip()

        settings = []
        with open(self.qsf) as f:
            for line in f.readlines():
                line = uncomment(line)
                if line:
                    settings.append(line)

        settings_mut = settings[:]
        yield settings_mut
        if settings_mut == settings:
            return

        settings_mut = set(settings_mut)
        gather = ""
        with open(self.qsf) as f:
            for line in f.readlines():
                content = uncomment(line)
                if not content:
                    gather += line
                elif content in settings_mut:
                    gather += line
                    settings_mut.remove(content)
        for setting in settings_mut:
            gather += setting + '\n'

        with open(self.qsf, 'w') as f:
            f.write(gather)

    def source_setting(self, path):
        _, ext = os.path.splitext(path)
        relpath = os.path.relpath(path, self.path)
        ext = ext.lower()
        if ext == '.v':
            return 'set_global_assignment -name VERILOG_FILE ' + relpath
        elif ext == '.qip':
            return 'set_global_assignment -name QIP_FILE ' + relpath
        elif ext == '.sdc':
            return 'set_global_assignment -name SDC_FILE ' + relpath
        else:
            raise RuntimeError('unknown source type: {}'.format(repr(ext)))
    
    def add_source(self, path):
        if not os.path.exists(path):
            raise RuntimeError('file does not exist: ' + path)
        setting = self.source_setting(path)
        with self.settings() as s:
            if not setting in s:
                s.append(setting)

    def rm_source(self, path):
        setting = self.source_setting(path)
        with self.settings() as s:
            if setting in s:
                s.remove(setting)
