# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

# pylint: disable=line-too-long
import argparse

from knack.arguments import ArgumentsContext, CLIArgumentType


class Flag:
    """ Place holder to be used for optionals that take 0 or more arguments """


# pylint: disable=too-many-statements
def load_arguments(self, _):

    modules_type = CLIArgumentType(nargs='*',
                                   help="Space-separated list of modules or extensions (dev mode) to check. "
                                        "Use 'CLI' to check built-in modules or 'EXT' to check extensions. "
                                        "Omit to check all. ")

    with ArgumentsContext(self, '') as c:
        c.argument('private', action='store_true', help='Target the private repo.')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true', help='Answer "yes" to all prompts.')
        c.argument('use_ext_index', action='store_true', help='Run command on extensions registered in the azure-cli-extensions index.json.')
        c.argument('git_source', options_list='--src', arg_group='Git', help='Name of the Git source branch to check (i.e. master or upstream/master).')
        c.argument('git_target', options_list='--tgt', arg_group='Git', help='Name of the Git target branch to check (i.e. dev or upstream/dev)')
        c.argument('git_repo', options_list='--repo', arg_group='Git', help='Path to the Git repo to check.')

    with ArgumentsContext(self, 'setup') as c:
        c.argument('cli_path', options_list=['--cli', '-c'], nargs='?', const=Flag, help="Path to an existing Azure CLI repo. Omit value to search for the repo or use special value 'EDGE' to install the latest developer edge build.")
        c.argument('ext_repo_path', options_list=['--repo', '-r'], nargs='+', help='Space-separated list of paths to existing Azure CLI extensions repos.')
        c.argument('ext', options_list=['--ext', '-e'], nargs='+', help="Space-separated list of extensions to install initially. Use '*' to install all extensions.")
        c.argument('deps', options_list=['--deps-from', '-d'], choices=['requirements.txt', 'setup.py'], default='requirements.txt', help="Choose the file to resolve dependencies.")

