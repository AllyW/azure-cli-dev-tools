# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.help_files import helps
# pylint: disable=line-too-long, anomalous-backslash-in-string


helps[''] = """
    short-summary: Development utilities for Azure CLI 2.0.
"""


helps['setup'] = """
    short-summary: Set up your environment for development of Azure CLI command modules and/or extensions.
    long-summary: Use --verbose to show the commands that are run, --debug to show the command output.
    examples:
        - name: Fully interactive setup.
          text: azdev setup

        - name: Install only the CLI in dev mode and search for the existing repo.
          text: azdev setup -c

        - name: Install public CLI and setup an extensions repo. Do not install any extensions.
          text: azdev setup -r azure-cli-extensions

        - name: Install CLI in dev mode, along with the extensions repo. Auto-find the CLI repo and install the `alias` extension in dev mode.
          text: azdev setup -c -r azure-cli-extensions -e alias

        - name: Install only the CLI in dev mode and resolve dependencies from setup.py.
          text: azdev setup -c -d setup.py
"""
