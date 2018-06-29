from __future__ import print_function
import sys
import os
import docopt
from bash import BashCompletion, ManualBashCompletion
from zsh import OhMyZshCompletion, ZshPreztoCompletion, ZshUsrShareCompletion, ZshCompletion
from common import DocoptCompletionException, parse_params

USAGE = """Usage:
    docopt-completion <docopt-script> [--manual-zsh | --manual-bash] [--read-stdin]
    docopt-completion --help

Options:
    --manual-zsh        Do not attempt to find completion paths automatically. Output ZSH completion file to local directory
    --manual-bash       Do not attempt to find completion paths automatically. Output BASH completion file to local directory
    --read-stdin        Read DocOpt from stdin rather than the executable --help call
"""

COMPLETION_PATH_USAGE = """No completion paths found.
docopt-completion only supports the following configurations:
{paths_help}
You may also generate the completion file and place it in a path known to your completion system, by running the command:
\tdocopt-completion <docopt-script> [--manual-zsh | --manual-bash]
For zsh, completion paths can be listed by running 'echo $fpath'"""

dat = """Usage:
  adventure.py PROJECT --lint BOOK [-v]
  adventure.py PROJECT --md BOOK [-o MDFILE]
  adventure.py PROJECT [--run] BOOK [-v] [-p PAGE] [-T SPERC] [-a MODE] [--tag TAGS...] [--skip SKIP...]
  adventure.py PROJECT [--run] BOOK [-v] [-P PAGES] [-T SPERC]

Options:
  --lint       Check the syntax of a book
  --md         Generate markdown file representation of a book.
  --run        Performs the commands in the adventure.
  -T SPERC     Test mode, commands are not actually performed, instead a dice is rolled
               for the outcome, with SPERC chance of success.
  -a MODE      Specifies automatic choice behavior based on previous command.
               Mode is one of: off, success, single, full [default: off]
  -o MDFILE    Optionally specify an output path for --md.
  -p PAGE      Specifies starting page, where PAGE is the starting page, by name or number
  --tag TAGS   Only include pages with any of the TAGS tag or name
  --skip SKIP  Skip pages with any of the SKIP tag or name
  -v           Be verbose.
  -P PAGES     Specify the pages to run by name or number. Any page failure, results in
               program termination with non-zero exit code.

Recommended BOOKs:
 * setup  Initialize or reconfigure a project.
 * build  Sync, build, edit your code, use daily.
 * fix    Bring a broken build or sync back in order.

Chatter:
 https://gus.lightning.force.com/lightning/r/0D5B000000dS1v9KAC/view

Short video introduction:
 https://drive.google.com/open?id=1tg7DLCzQHWYXo2DcfX95hDxBILHtmOBW


"""

def _generate_paths_help(generators):
    output = ""
    for generator in generators:
        output += "\t{}. The path {} must exist.\n".format(generator.get_name(), generator.get_completion_path())
    return output

def _autodetect_generators():
    completion_generators = [OhMyZshCompletion(),
                             ZshPreztoCompletion(),
                             ZshUsrShareCompletion(),
                             BashCompletion()]
    generators_to_use = [generator for generator in completion_generators if generator.completion_path_exists()]

    if len(generators_to_use) == 0:
        paths_help = _generate_paths_help(completion_generators)
        raise DocoptCompletionException(COMPLETION_PATH_USAGE.format(paths_help=paths_help))

    return generators_to_use

def docopt_completion(cmd, manual_zsh=False, manual_bash=False, doc=None):
    generators_to_use = []
    if manual_zsh:
        generators_to_use.append(ZshCompletion())
    if manual_bash:
        generators_to_use.append(ManualBashCompletion())
    else:
        generators_to_use = _autodetect_generators()

    param_tree, option_help = parse_params(cmd, doc)

    for generator in generators_to_use:
        generator.generate(cmd, param_tree, option_help)


def main():
    arguments = docopt.docopt(USAGE)
    cmd = arguments["<docopt-script>"]
    manual_bash = arguments["--manual-bash"]
    manual_zsh = arguments["--manual-zsh"]
    try:
        docopt_completion(cmd, manual_zsh, manual_bash)
    except DocoptCompletionException as e:
        print(e.args[0])
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
