from __future__ import annotations

import hashlib
from collections.abc import Generator
from functools import reduce
from typing import Any, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


def diff_configs(
    config1: dict[K, V], config2: dict[K, V]
) -> list[tuple[K, Optional[V], Optional[V]]]:
    """See what the differences are from config1 to config2. Input 2 config dicts and it will output
    a list of (key, value_from, value_to)

    e.g. [ (device.frequency, 10, 100) ] means the device
    frequency was 10 in config1 and 100 in config2.

    (a.b, None, 2) Means it wasn't present in config1 but now has the value 2
    (a.b, 2, None) Means it did have the value 2 but it now no longer exists

    :param dict config1: Config in dict form (see `load_config`)
    :param dict config2: Config in dict form (see `load_config`)
    :returns: [ (attribute, old value, new value) ]
    :rtype: list of tuples

    """

    # Lists cannot be turned into set elements. Convert to strings for testing
    def to_set(config):
        ret = set()
        for k, v in recursive_dict_iter(config):
            if isinstance(v, list):
                ret.add((k, str(v)))
            else:
                ret.add((k, v))
        return ret

    c1_set = to_set(config1)
    c2_set = to_set(config2)

    # c1/c2_set will be a set of (device.promethion.int_cap, 2) tuples
    # Get the differences from config1->config2
    # If the values are different then the tuples will be different
    key_value_diff_1 = c1_set.difference(c2_set)
    # Grab just the keys that have changed.
    key_diff_1 = {item[0] for item in key_value_diff_1}

    # Do same for config2->config1
    key_value_diff_2 = c2_set.difference(c1_set)
    key_diff_2 = {item[0] for item in key_value_diff_2}

    key_diffs = key_diff_1.union(key_diff_2)

    # For each key that's changed, find the value in config1 and config2
    changes = [
        (key, find_path(key, config1), find_path(key, config2)) for key in key_diffs
    ]
    return changes


def recursive_dict_iter(dictionary: dict, path: str = "") -> Generator[Any, None, None]:
    """Allows iteration over all key, value pairs recursively in dictionaries.
    It will yield (path, value) where path gives the path to that item.
    E.g. {a: 1, b: {c: 2, d: 3}} would give (a, 1) then (b.c, 2) then (b.d, 3)

    :param dict dictionary: Dictionary to recursively iterate over
    :param str path: prefix to add to keys
    :returns: An iterable to loop over all (key, value)
    :rtype: generator

    """
    for key, value in dictionary.items():
        new_path = key
        if path != "":
            new_path = path + "." + key

        if not isinstance(value, dict):
            yield (new_path, value)
        else:
            # Change to yield from recursive_dict... in python3
            for item in recursive_dict_iter(value, path=new_path):
                yield item


def create_path(path: str, dictionary: dict) -> dict:
    """Make sure that path exists in the dictionary, creating empty dictionaries on the way

    :param path: Path to create
    :param dictionary: Object to create path in
    """
    if not path:
        return dictionary

    current = dictionary
    for key in path.split("."):
        if key not in current:
            current[key] = {}
        current = current[key]

    return dictionary


def find_path(path: str, dictionary: dict) -> Optional[Any]:
    """Lookup a path e.g. 'a.b' in dict: {'a': {'b': 2}} will return 2.
    If the path doesn't exist, None is returned

    :param str path: Path to lookup in a hierarchical dictionary
    :param dict dictionary: Dictionary to look up path in
    :returns: The item stored at that path in the dict
    :rtype: item
    :raises AttributeError: If the path is not there
    """
    try:
        if not path:
            return dictionary
        return reduce(lambda d, k: d.get(k), path.split("."), dictionary)  # type: ignore Except is below
    except AttributeError:
        return None


def set_path(path: str, dictionary: dict, value: Any) -> None:
    """Lookup path in dictionary and assign it to value.
        This will create the path if it doesn't exist

    :param path: dot string path of which dict to look up
    :param dictionary: Dict to look in
    :param value: Value to store at location

    """
    if not path:
        return

    create_path(path, dictionary)

    current = dictionary
    lookup = path.split(".")[:-1]
    final_key = path.split(".")[-1]

    for key in lookup:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[final_key] = value


def recursive_merge(dict1: dict, dict2: dict) -> None:
    """Does an iterative version of dict1.update(dict2).

    :param dict dict1: Dictionary that will be altered
    :param dict dict2: Dictionary that items will be pulled from
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            # If dictionary, recurse
            recursive_merge(dict1[key], value)
        else:
            dict1[key] = value
