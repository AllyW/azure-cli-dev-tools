#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Azure Command Diff Tools package that can be installed using setuptools"""

from setuptools import setup, find_packages


with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(name="azure-cli-diff-tool",
      version='0.0.1',
      description="A tool for cli metadata management",
      long_description=README + '\n\n' + HISTORY,
      license='MIT',
      author='Microsoft Corporation',
      author_email='azpycli@microsoft.com',
      packages=find_packages(),
      include_package_data=True,
      install_requires=["deepdiff", "requests"],
      package_data={
        "azureCliDiffTool": ["data/*"]
      }
      )
