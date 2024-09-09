# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import os
import traceback

from knack.log import get_logger
from knack.util import CLIError

from azdev.utilities import cmd
from azdev.utilities import display
from azure.cli.core import get_default_cli

logger = get_logger(__name__)
os.environ['AZURE_CORE_COLLECT_TELEMETRY'] = 'False'


class ProfileContext:
    def __init__(self, profile_name=None):
        self.target_profile = profile_name

        self.origin_profile = current_profile()

    def __enter__(self):
        if self.target_profile is None or self.target_profile == self.origin_profile:
            display('The tests are set to run against current profile "{}"'.format(self.origin_profile))
        else:
            display('Switching to target profile "{}"...'.format(self.target_profile))
            cli = get_default_cli()
            cli.invoke(["cloud", "update", "--profile", self.target_profile], out_file=open(os.devnull, 'w'))
            if cli.result.error:
                raise CLIError(cli.result.error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.target_profile is not None and self.target_profile != self.origin_profile:
            display('Switching back to origin profile "{}"...'.format(self.origin_profile))
            cli = get_default_cli()
            cli.invoke(["cloud", "update", "--profile", self.origin_profile], out_file=open(os.devnull, 'w'))

        if exc_tb:
            display('')
            traceback.print_exception(exc_type, exc_val, exc_tb)


def current_profile():
    return cmd('az cloud show --query profile -otsv', show_stderr=False).result
