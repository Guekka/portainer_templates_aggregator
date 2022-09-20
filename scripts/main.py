"""
This script downloads portainer templates from several trusted sources and merges them.
It is meant to run periodically.
"""

import json
import requests

from dataclasses import dataclass
from typing import Dict, List, Any

CONFIG_PATH = "scripts/configuration.json"
TEMPLATE_VERSION = 2
TITLE = "title"

TemplateList = List[Any]
JSON = Dict[str, Any]


@dataclass
class Config:
    template_lists: List[str]
    output_file: str


def load_config(path: str) -> Config:
    with open(path) as conf_file:
        return Config(**json.load(conf_file))


def retrieve_templates(url: str) -> TemplateList:
    res = requests.get(url)
    if res.status_code != 200:
        print(f"Cannot reach {url}")
        return []

    json_data = json.loads(res.text)
    version = json_data.get("version", -1)
    if int(version) != TEMPLATE_VERSION:
        print(f"Wrong version for template {url}: {version}")
        return []

    return json_data.get("templates", [])


def clean_up_string(s: str) -> str:
    # The TITLE data is cleaned up in order to improve detection
    # We are only keeping letters or numbers

    def filter_pred(c: str):
        return c.isalpha() or c.isdigit()

    return ''.join(filter(filter_pred, s.lower()))


def is_duplicate(current: TemplateList, new_template: JSON) -> bool:
    # This is the most "complicated" part
    # Here, we try to eliminate duplicates
    # Nothing too fancy, we just compare by TITLE for now

    # Cache the cleaned up title
    new_title = clean_up_string(new_template[TITLE])

    # This is not best for performance, but we're just going to go the O(n²) way
    # It should be enough for our purpose
    for cur_template in current:
        if clean_up_string(cur_template[TITLE]) == new_title:
            return True
    return False


def merge_templates(result: TemplateList, new: TemplateList) -> TemplateList:
    for template in new:
        if not is_duplicate(result, template):
            result.append(template)

    return result


def save_json(templates: TemplateList) -> str:
    result = {"version": f"{TEMPLATE_VERSION}", "templates": templates}
    return json.dumps(result, indent=4)


def main():
    config = load_config(CONFIG_PATH)

    result: TemplateList = []
    for url in config.template_lists:
        template = retrieve_templates(url)
        result = merge_templates(result, template)

    # We're not going to leave this huge list unsorted, are we?
    result = sorted(result, key=lambda t: t[TITLE])

    # We're done!
    with open(config.output_file, "w") as out:
        out.write(save_json(result))


if __name__ == '__main__':
    main()
