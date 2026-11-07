import os
from glob import glob
from typing import Any, Dict, List, Union

from pyUltroid import *
from pyUltroid.fns.tools import translate

try:
    from yaml import safe_load
except ModuleNotFoundError:
    from pyUltroid.fns.tools import safe_load

# Persian is the default for this fork. An explicit DB/environment setting wins.
ULTConfig.lang = udB.get_key("language") or os.getenv("LANGUAGE", "fa")

languages = {}
PATH = "strings/strings/{}.yml"


def load(file):
    if not file.endswith(".yml") or not os.path.exists(file):
        return
    code = os.path.basename(file)[:-4]
    try:
        with open(file, encoding="UTF-8") as stream:
            data = safe_load(stream) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Invalid language file: {file}")
        languages[code] = data
    except Exception as er:
        LOGS.info(f"Error in {file[:-4]} language file")
        LOGS.exception(er)


# English is always loaded as the fallback, even when Persian is selected.
load(PATH.format("en"))
if ULTConfig.lang != "en":
    load(PATH.format(ULTConfig.lang))


def get_string(key: str, _res: bool = True) -> Any:
    lang = ULTConfig.lang or "en"
    selected = languages.get(lang, {})
    value = selected.get(key)
    if value is not None:
        return value

    english = languages.get("en", {}).get(key)
    if english is None:
        if not _res:
            return None
        return f"Warning: could not load any string with the key `{key}`"

    if lang == "en":
        return english

    try:
        translated = translate(english, lang_tgt=lang).replace(r"\ N", "\n")
        if translated.count("{}") != english.count("{}"):
            translated = english
    except Exception as er:
        LOGS.exception(er)
        translated = english

    languages.setdefault(lang, {})[key] = translated
    return translated


def get_help(key):
    doc = get_string(f"help_{key}", _res=False)
    if doc:
        return get_string("cmda") + doc


def get_languages() -> Dict[str, Union[str, List[str]]]:
    for file in glob("strings/strings/*.yml"):
        load(file)
    return {
        code: {
            "name": languages[code].get("name", code),
            "natively": languages[code].get("natively", code),
            "authors": languages[code].get("authors", []),
        }
        for code in languages
    }
