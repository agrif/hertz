import subprocess
import sys
from . import command, init, source, build, program

if __name__ == "__main__":
    try:
        command.recurse(*sys.argv[1:])
    except subprocess.CalledProcessError as e:
        sys.exit(1)

