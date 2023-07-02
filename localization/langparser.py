import json
import inspect
import os


def split_path(path: str):
    elements = []

    # Split the path into components
    while True:
        path, tail = os.path.split(path)
        if tail:
            elements.insert(0, tail)
        else:
            if path:
                elements.insert(0, path)
            break
    return elements


class LangParser:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LangParser, cls).__new__(cls)
        return cls._instance

    def __init__(self, localizations: dict, project_root: str, language: str = "English"):
        self.project_root = project_root
        self.language = language
        self.localization_dict = localizations

        with open(self.localization_dict.get("English")) as f:
            self.english: dict = json.load(f)

        with open(self.localization_dict.get(language, "localization/english.json")) as localizations_json:
            self.localization: dict = json.load(localizations_json)

    def get_key(self, caller_file: str, key: str):
        # function to get the key from the localization dict
        # based on the caller file

        caller_file = caller_file.rstrip(".py")
        split_caller = split_path(caller_file)
        split_project_root = split_path(self.project_root)
        key_elements = [x for x in split_caller if x not in split_project_root]
        # TODO: this might error out when the root path has strings that are also present in the split caller
        subdict = self.localization["localizations"]

        for element in key_elements:
            subdict = subdict[element]

        return subdict.get(key)

    def change_localization(self, language: str):
        with open(self.localization_dict.get(language, "localization/english.json")) as localizations_json:
            self.localization: dict = json.load(localizations_json)

    def parse_message(self, message_code: str, *args):
        caller_file = inspect.currentframe().f_back.f_code.co_filename
        message_to_format = self.get_key(caller_file, message_code)

        if not message_to_format:
            message_to_format = self.english["localizations"].get(message_code, message_code)

        return message_to_format.format(*args)

    def parse_message_as(self, parse_as: str, message_code: str, *args):
        """
        parse_as: Is the caller file to emulate
        example: "src/cli/ui.py"
        or if running from "/users/username/Downloads/OCSysInfo", you can also use
         "/users/username/Downloads/OCSysInfo/src/cli/ui.py"
        """

        key = self.get_key(parse_as, message_code)

        return key.format(*args)