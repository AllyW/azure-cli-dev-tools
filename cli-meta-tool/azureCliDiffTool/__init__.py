# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
import os
import json
from enum import Enum
import logging
from deepdiff import DeepDiff
from .meta_change_detect import MetaChangeDetect
from .utils import get_blob_config, load_blob_config_file, get_target_version_modules, \
    extrct_module_name_from_meta_file, export_meta_changes_to_csv, export_meta_changes_to_json, \
    export_meta_changes_to_dict


logger = logging.getLogger(__name__)


class DiffExportFormat(Enum):
    DICT = "dict"
    TEXT = "text"
    TREE = "tree"


def diff_export_format_choices():
    return [form.value for form in DiffExportFormat]


def meta_diff(base_meta_file, diff_meta_file, only_break=False, output_type="text", output_file=None):
    if not os.path.exists(base_meta_file):
        raise Exception("base meta file needed")
    if not os.path.exists(diff_meta_file):
        raise Exception("diff meta file needed")

    with open(base_meta_file, "r") as g:
        command_tree_before = json.load(g)
    with open(diff_meta_file, "r") as g:
        command_tree_after = json.load(g)
    diff = DeepDiff(command_tree_before, command_tree_after)
    if not diff:
        print(f"No meta diffs from {diff_meta_file} to {base_meta_file}")
        return export_meta_changes_to_json(None, output_file)
    else:
        detected_changes = MetaChangeDetect(diff, command_tree_before, command_tree_after)
        detected_changes.check_deep_diffs()
        result = detected_changes.export_meta_changes(only_break, output_type)
        return export_meta_changes_to_json(result, output_file)


def version_diff(base_version, diff_version, only_break=False, version_diff_file=None, use_cache=False,
                 output_type="dict", target_module=None):
    config = load_blob_config_file()
    blob_url, path_prefix, index_file = get_blob_config(config)
    base_version_module_list = get_target_version_modules(blob_url, path_prefix, index_file, base_version, use_cache)
    get_target_version_modules(blob_url, path_prefix, index_file, diff_version, use_cache)
    version_diffs = []
    for _, base_meta_file_full_path, base_meta_file in base_version_module_list:
        module_name = extrct_module_name_from_meta_file(base_meta_file)
        if not module_name:
            continue
        if target_module and module_name != target_module:
            continue
        diff_meta_file_full_path = os.path.join(os.getcwd(), path_prefix + diff_version, base_meta_file)
        if not os.path.exists(diff_meta_file_full_path):
            print(f"Module {module_name} removed for {diff_version}")
            continue
        with open(base_meta_file_full_path, "r") as g:
            command_tree_before = json.load(g)
        with open(diff_meta_file_full_path, "r") as g:
            command_tree_after = json.load(g)
        diff = DeepDiff(command_tree_before, command_tree_after)
        if not diff:
            print(f"No meta diffs from version: {diff_version}/{base_meta_file} for module: {module_name}")
            continue
        detected_changes = MetaChangeDetect(diff, command_tree_before, command_tree_after)
        detected_changes.check_deep_diffs()
        diff_objs = detected_changes.export_meta_changes(only_break, "dict")
        mod_obj = {"module": module_name}
        for obj in diff_objs:
            obj.update(mod_obj)
            version_diffs.append(obj)
    if output_type == "dict":
        return export_meta_changes_to_dict(version_diffs, version_diff_file)
    return export_meta_changes_to_csv(version_diffs, version_diff_file)
