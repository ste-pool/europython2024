import tomllib
import pathlib
import pprint
from config_utils import set_path


def load_config(path, import_base=None):
    """Made the decision here to use paths relative to the first config
    loaded. You will need to tweak if you want it relative to something else.
    Another assumption built in is that when you load the config you put
    it nested inside the import rather than import that section.
    You may also want to consider what happens if you have something similar to this:

    [x]
    import = "test.toml"
    y = 2

    And what you want to do with that. You could just do a recursive merge from
    the import. For this simple example, we just assume that "import" is the only
    key if it exists.
    """
    with open(path, "rb") as config:
        data = tomllib.load(config)

    import_base = import_base or path.parent.absolute()

    look_in_dict = [("", data)]
    while look_in_dict:
        path, path_data = look_in_dict.pop()
        for key, value in path_data.items():
            if key == "import":
                if len(path_data) != 1:
                    raise RuntimeError(
                        f"Path {path or '.'} contains more than 'import'"
                    )

                value = load_config(pathlib.Path(import_base / value), import_base)
                set_path(path, data, value)
            if isinstance(value, dict):
                look_in_dict.append((f"{path}.{key}" if path else key, value))

    return data


pprint.pprint(load_config(pathlib.Path("configs/base.toml")))
