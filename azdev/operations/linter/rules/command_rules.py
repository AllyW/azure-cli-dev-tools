# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from ..rule_decorators import CommandRule
from ..linter import RuleError, LinterSeverity
from ..util import has_illegal_html_tag, has_broken_site_links
from azdev.operations.constant import DISALLOWED_HTML_TAG_RULE_LINK, BROKEN_LINK_RULE_LINK

@CommandRule(LinterSeverity.HIGH)
def missing_command_help(linter, command_name):
    if not linter.get_command_help(command_name) and not linter.command_expired(command_name):
        raise RuleError('Missing help')


@CommandRule(LinterSeverity.HIGH)
def no_ids_for_list_commands(linter, command_name):
    if command_name.split()[-1] == 'list' and 'ids' in linter.get_command_parameters(command_name):
        raise RuleError('List commands should not expose --ids argument')


@CommandRule(LinterSeverity.HIGH)
def expired_command(linter, command_name):
    if linter.command_expired(command_name):
        raise RuleError('Deprecated command is expired and should be removed.')


@CommandRule(LinterSeverity.LOW)
def group_delete_commands_should_confirm(linter, command_name):
    # We cannot detect from cmd table etc whether a delete command deletes a collection, group or set of resources.
    # so warn users for every delete command.

    if command_name.split()[-1].lower() == "delete":
        if 'yes' not in linter.get_command_parameters(command_name):
            raise RuleError("If this command deletes a collection, or group of resources. "
                            "Please make sure to ask for confirmation.")

@CommandRule(LinterSeverity.HIGH)
def disallowed_html_tag_from_command(linter, command_name):
    if command_name == '' or not linter.get_loaded_help_entry(command_name):
        return
    help_entry = linter.get_loaded_help_entry(command_name)
    if help_entry.short_summary and has_illegal_html_tag(help_entry.short_summary):
        raise RuleError("Command '{}' has disallowed html tags in short summary. "
                        "If tag is a placeholder, please wrap it with backtick. "
                        "For more info please refer to: {}".format(command_name, DISALLOWED_HTML_TAG_RULE_LINK))
    if help_entry.long_summary and has_illegal_html_tag(help_entry.long_summary):
        raise RuleError("Command '{}' has disallowed html tags in long summary. "
                        "If tag is a placeholder, please wrap it with backtick. "
                        "For more info please refer to: {}".format(command_name, DISALLOWED_HTML_TAG_RULE_LINK))


@CommandRule(LinterSeverity.HIGH)
def broken_site_link_from_command(linter, command_name):
    if command_name == '' or not linter.get_loaded_help_entry(command_name):
        return
    help_entry = linter.get_loaded_help_entry(command_name)
    if help_entry.short_summary and has_broken_site_links(help_entry.short_summary):
        raise RuleError("Command '{}' has broken links in short summary. "
                        "If link is an example, please wrap it with backtick. "
                        "For more info please refer to: {}".format(command_name, BROKEN_LINK_RULE_LINK))
    if help_entry.long_summary and has_broken_site_links(help_entry.long_summary):
        raise RuleError("Command '{}' has broken links in long summary. "
                        "If link is an example, please wrap it with backtick. "
                        "For more info please refer to: {}".format(command_name, BROKEN_LINK_RULE_LINK))