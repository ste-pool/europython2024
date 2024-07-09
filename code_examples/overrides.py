import tomllib
import pprint
from config_utils import recursive_merge


def load_config(path, overrides):
    with open(path, "rb") as config:
        data = tomllib.load(config)

    look_in_dict = [("", data)]
    while look_in_dict:
        path, path_data = look_in_dict.pop()
        for key, value in list(path_data.items()):
            if key == "override":
                for override in value:
                    if overrides[override.pop("when").pop("type")]:
                        recursive_merge(path_data, override)
                path_data.pop(key)
            elif isinstance(value, dict):
                look_in_dict.append((f"{path}.{key}" if path else key, value))
    return data


pprint.pprint(load_config("configs/overrides.toml", overrides={"fan": True}))
pprint.pprint(load_config("configs/overrides.toml", overrides={"fan": False}))
