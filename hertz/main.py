from . import command, init

if __name__ == "__main__":    
    args = command.parser.parse_args()
    Cmd = command.subcommands[args.subcommand]
    c = Cmd()
    c.run(args)
