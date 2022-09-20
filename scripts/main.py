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
SORT_FIELD = "title"

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


def merge_templates(result: TemplateList, new: TemplateList) -> TemplateList:
    # This is the most "complicated" part
    # Here, we try to eliminate duplicates
    # Nothing too fancy, we just compare by SORT_FIELD for now

    # This is not best for performance, but we're just going to go the O(n²) way

    def contains(sort_field: str):
        for template in result:
            if template[SORT_FIELD] == sort_field:
                return True
        return False

    for template in new:
        if not contains(template[SORT_FIELD]):
            result.append(template)

    return result


def save_json(templates: TemplateList) -> str:
    result = {"version": TEMPLATE_VERSION, "templates": templates}
    return json.dumps(result, indent=4)


def main():
    config = load_config(CONFIG_PATH)

    result: TemplateList = []
    for url in config.template_lists:
        template = retrieve_templates(url)
        result = merge_templates(result, template)

    # We're not going to leave this huge list unsorted, are we?
    result = sorted(result, key=lambda t: t[SORT_FIELD])

    # We're done!
    with open(config.output_file, "w") as out:
        out.write(save_json(result))


if __name__ == '__main__':
    main()
