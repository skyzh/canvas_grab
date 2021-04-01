import argparse
from .version import VERSION
from termcolor import colored
from pathlib import Path
from .config import Config
import toml


def greeting():
    # First, welcome our users
    print("Thank you for using canvas_grab!")
    print(
        f'You are using version {VERSION}. If you have any questions, please file an issue at {colored("https://github.com/skyzh/canvas_grab/issues", "blue")}')
    print(
        f'You may review {colored("README.md", "green")} and {colored("LICENSE", "green")} shipped with this release')
    print(
        f'You may run this code with argument {colored(f"-h","cyan")} for command line usage')
    print('--------------------')


def get_options():
    # Argument Parser initiation

    parser = argparse.ArgumentParser(
        description='Grab all files on Canvas LMS to local directory.',
        epilog="Configuration file variables specified with program arguments will override the "
        "original settings at runtime, but will not be written to the original configuration file. "
        "If you specify a configuration file with the --config-file argument when you configure it, "
        "it will be overwritten with the new content.")

    # Interactive
    interactive_group = parser.add_mutually_exclusive_group()
    interactive_group.add_argument("-i", "--interactive", dest="interactive", action="store_true",
                                   default=True,
                                   help="Set the program to run in interactive mode (default action)")
    interactive_group.add_argument("-I", "--non-interactive", "--no-input", dest="interactive",
                                   action="store_false", default=True,
                                   help="Set the program to run in non-interactive mode. This can be "
                                   "used to exit immediately in case of profile corruption without "
                                   "getting stuck with the input.")

    # Reconfiguration
    parser.add_argument("-r", "--reconfigure", "--configure", dest="reconfigure",
                        help="Reconfigure the tool.", action="store_true")

    # Location Specification
    parser.add_argument("-o", "--download-folder", "--output",
                        dest="download", help="Specify alternative download folder.")
    parser.add_argument("-c", "--config-file", dest="config_file", default="config.toml",
                        help="Specify alternative configuration file.")

    # Generic Options
    # TODO quiet mode
    # parser.add_argument("-q", "--quiet", dest="quiet", help="Start the program in quiet mode. "
    #                     "Only errors will be printed.", action="store_true")
    parser.add_argument("--version", action="version",
                        version=VERSION)
    parser.add_argument("-k", "--keep-version", "--no-update", dest="noupdate", action="store_true",
                        default=False, help="Skip update checking. This will be helpful without "
                        "a stable network connection and prevent reconfiguration.")

    args = parser.parse_args()

    # TODO quiet mode
    greeting()

    print(f'Using config {args.config_file}')
    config_file = Path(args.config_file)
    config = Config()
    config_fail = False
    if config_file.exists():
        try:
            config.from_config(toml.loads(
                config_file.read_text(encoding='utf8')))
        except KeyError as e:
            print(
                f'It seems that you have upgraded canvas_grab. Please reconfigure. ({colored(e, "red")} not found)')
            config_fail = True
    if config_fail or args.reconfigure or not config_file.exists():
        if not args.interactive:
            print(
                "configuration file corrupted or not exist, and non interactive flag is set. Quit immediately.")
            exit(-1)
        try:
            config.interact()
        except KeyboardInterrupt:
            print("User canceled the configuration process")
            return
        config_file.write_text(
            toml.dumps(config.to_config()), encoding='utf8')
    if args.download:
        config.download_folder = args.download

    return args.interactive, args.noupdate, config
