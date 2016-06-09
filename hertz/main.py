import subprocess
import sys
from . import command, init, source, build

if __name__ == "__main__":    
    args = command.parser.parse_args()
    Cmd = command.subcommands[args.subcommand]
    try:
        Cmd(args)
    except subprocess.CalledProcessError as e:
        sys.exit(1)
