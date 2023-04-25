# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
import os
import re
from enum import Enum
import jsbeautifier
from azure.cli.core.aaz import has_value
from knack.log import get_logger

logger = get_logger(__name__)

CMD_NAME_PATTERN = re.compile(r"\[\'commands\'\]\[\'([a-zA-Z0-9\-\s]+)\'\]")
CMD_PARAMETER_PROPERTY_PATTERN = re.compile(r"\[(.*?)\]")


class ChangeType(int, Enum):
    DEFAULT = 0
    ADD = 1
    CHANGE = 2
    REMOVE = 3

def get_command_tree(command_name):
    """
    input: monitor log-profiles create
    ret:
    {
        is_group: True,
        group_name: 'monitor',
        sub_info: {
            is_group: True,
            group_name: 'monitor log-profiles',
            sub_info: {
                is_group: False,
                cmd_name: 'monitor log-profiles create'
            }
        }
    }
    """
    name_arr = command_name.split()
    ret = {}
    name_arr.reverse()
    for i, name in enumerate(name_arr):
        tmp = {}
        if i == 0:
            tmp = {
                "is_group": False,
                "cmd_name": " ".join(name_arr[::-1])
            }
        else:
            tmp = {
                "is_group": True,
                "group_name": " ".join(name_arr[len(name_arr):i-1:-1]),
                "sub_info": ret
            }
        ret = tmp
    return ret


def process_aaz_argument(az_arguments_schema, argument_settings, para):
    _fields = az_arguments_schema._fields
    aaz_type = _fields.get(argument_settings["dest"], None)
    if aaz_type:
        para["aaz_type"] = aaz_type.__class__.__name__
        para["type"] = aaz_type._type_in_help
        if has_value(aaz_type._default):
            para["aaz_default"] = aaz_type._default
        if para["aaz_type"] in ["AAZArgEnum"] and aaz_type.get("enum", None) and aaz_type.enum.get("items", None):
            para["aaz_choices"] = aaz_type.enum["items"]


def gen_command_meta(command_info, with_help=False, with_example=False):
    stored_property_when_exist = ["confirmation", "supports_no_wait", "is_preview"]
    command_meta = {
        "name": command_info["name"],
        "is_aaz": command_info["is_aaz"],
    }
    for prop in stored_property_when_exist:
        if command_info[prop]:
            command_meta[prop] = command_info[prop]
    if with_example:
        try:
            command_meta["examples"] = command_info["help"]["examples"]
        except Exception as e:
            pass
    if with_help:
        try:
            command_meta["desc"] = command_info["help"]["short-summary"]
        except Exception as e:
            pass
    parameters = []
    for key, argument in command_info["arguments"].items():
        if argument.type is None:
            continue
        settings = argument.type.settings
        para = {
            "name": settings["dest"],
            "options": sorted(settings["options_list"])
        }
        if settings.get("required", False):
            para["required"] = True
        if settings.get("choices", None):
            para["choices"] = sorted(list(settings["choices"]))
        if settings.get("id_part", None):
            para["id_part"] = settings["id_part"]
        if settings.get("nargs", None):
            para["nargs"] = settings["nargs"]
        if settings.get("default", None):
            para["default"] = settings["default"]
        if with_help:
            para["desc"] = settings["help"]
        if command_info["is_aaz"] and command_info["az_arguments_schema"]:
            process_aaz_argument(command_info["az_arguments_schema"], settings, para)
        parameters.append(para)
    command_meta["parameters"] = parameters
    return command_meta


def get_commands_meta(command_group_table, commands_info, with_help, with_example):
    commands_meta = {}

    for command_info in commands_info:
        moduel_name = command_info["source"]["module"]
        command_name = command_info["name"]
        if moduel_name not in commands_meta:
            commands_meta[moduel_name] = {
                "module_name": moduel_name,
                "name": "az",
                "commands": {},
                "sub_groups": {}
            }
        command_group_info = commands_meta[moduel_name]
        command_tree = get_command_tree(command_name)
        while True:
            if "is_group" not in command_tree:
                break
            if command_tree["is_group"]:
                group_name = command_tree["group_name"]
                if group_name not in command_group_info["sub_groups"]:
                    group_info = command_group_table.get(group_name, None)
                    command_group_info["sub_groups"][group_name] = {
                        "name": group_name,
                        "commands": {},
                        "sub_groups": {}
                    }
                    if with_help:
                        try:
                            command_group_info["sub_groups"][group_name]["desc"] = group_info.help["short-summary"]
                        except Exception as e:
                            pass

                command_tree = command_tree["sub_info"]
                command_group_info = command_group_info["sub_groups"][group_name]
            else:
                if command_name in command_group_info["commands"]:
                    logger.warning("repeated command: {0}".format(command_name))
                    break
                command_meta = gen_command_meta(command_info, with_help, with_example)
                command_group_info["commands"][command_name] = command_meta
                break
    return commands_meta


def gen_commands_meta(commands_meta, meta_output_path=None):
    options = jsbeautifier.default_options()
    options.indent_size = 4
    for key, module_info in commands_meta.items():
        file_name = "az_" + key + "_meta.json"
        if meta_output_path:
            file_name = meta_output_path + file_name
        file_folder = os.path.dirname(file_name)
        if file_folder and not os.path.exists(file_folder):
            os.makedirs(file_folder)
        with open(file_name, "w") as f_out:
            f_out.write(jsbeautifier.beautify(json.dumps(module_info), options))


def extract_cmd_name(key):
    cmd_name_res = re.finditer(CMD_NAME_PATTERN, key)
    if not cmd_name_res:
        return False, None
    for cmd_match in cmd_name_res:
        cmd_name = cmd_match.group(1)
        return True, cmd_name


def extract_cmd_property(key, cmd_name):
    cmd_key_pattern = re.compile(cmd_name + r"\'\]\[\'([a-zA-Z0-9\-\_]+)\'\]")
    cmd_key_res = re.findall(cmd_key_pattern, key)
    if not cmd_key_res:
        return False, None
    return True, cmd_key_res[0]


def extract_para_info(key):
    parameters_ind = key.find("['parameters']")
    property_ind = key.find("[", parameters_ind + 1)
    property_res = re.findall(CMD_PARAMETER_PROPERTY_PATTERN, key[property_ind:])
    if not property_res:
        return None
    return property_res


def export_meta_changes_to_json(output, output_file):
    output_file_folder = os.path.dirname(output_file)
    if not os.path.exists(output_file_folder):
        os.makedirs(output_file_folder)
    with open(output_file, "w") as f_out:
        f_out.write(json.dumps(output, indent=4))



if __name__ == '__main__':
    test_key = "root['sub_groups']['monitor']['sub_groups']['monitor private-link-scope']['sub_groups']['monitor private-link-scope scoped-resource']['commands']['monitor private-link-scope scoped-resource list']['is_preview']"
    test_key = "root['sub_groups']['monitor']['sub_groups']['monitor private-link-scope']['sub_groups']['monitor private-link-scope scoped-resource']['commands']['monitor private-link-scope scoped-resource list']['parameters'][0]['options'][1]"
    print(test_key)
    has_cmd, c_name = extract_cmd_name(test_key)
    print(has_cmd)
    print(c_name)
    has_cmd_key, cmd_key = extract_cmd_property(test_key, c_name)
    print(has_cmd_key)
    print(cmd_key)
    para_res = extract_para_info(test_key)
    print(para_res)