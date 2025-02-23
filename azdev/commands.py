# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.commands import CommandGroup

# pylint: disable=too-many-statements
def load_command_table(self, _):

    def operation_group(name):
        return 'azdev.operations.{}#{{}}'.format(name)

    with CommandGroup(self, '', operation_group('setup')) as g:
        g.command('setup', 'setup')
