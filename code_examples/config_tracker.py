from config_utils import recursive_dict_iter


# Main entrypoint is create a class then use that
class ConfigTracker(dict):
    def __init__(self, *args, **kwargs):
        self._parent = None  # Store the next level up in the dict

        # Deal with if the arg passed is one of ourselves (Nothing to do)
        if len(args) == 1 and isinstance(args[0], ConfigTracker):
            super().__init__(*args, **kwargs)

        # Deal with if the arg passed is a dict (Make it one of us - Recursively)
        elif len(args) == 1:
            for k, v in args[0].items():
                if isinstance(v, dict):
                    self.__setitem__(k, ConfigTracker(v))
                else:
                    self.__setitem__(k, v)

        self._accessed = set()

    def _access(self, x):
        # Record an access, and propagate up to parent
        self._accessed.add(x)

        if self._parent:
            self._parent[0]._access(f"{self._parent[1]}.{x}")

    def get(self, x, default=None):
        self._access(x)
        return super().get(x, default)

    def pop(self, x, default=None):
        self._access(x)
        return super().pop(x, default)

    def update(self, x):
        # When an update occurs, we want to follow the one supplied rather than ours
        super().update(x)
        if isinstance(x, ConfigTracker):
            self.recursive_merge_access(x)

    def __setitem__(self, k, v):
        if isinstance(v, ConfigTracker):
            v._parent = (self, k)
        super().__setitem__(k, v)

    def __getitem__(self, x):
        self._access(x)
        return super().__getitem__(x)

    def accessed(self):
        return self._accessed


# Create a dict and a "TrackedDict" that you would pass to the main() method
main_dict = {"a": {"b": 1, "c": 2, "d": 3}, "e": {"f": 4, "g": 5}}
tracked_dict = ConfigTracker(main_dict)

# Access some values in the tracked config
print(f"Looking at a.b {tracked_dict['a']['b']}")
a = tracked_dict["a"]
e = tracked_dict["e"]
print(f"Looking at e.f {tracked_dict['e']['f']}")
print(f"Looking at e.g {e.pop('g')}")

# Get the paths that have not been accessed
looked_at = tracked_dict.accessed()
actual = {k for k, v in recursive_dict_iter(main_dict)}

print(f"Keys accessed: {sorted(looked_at)}")
print(f"Keys not looked at: {sorted(actual.difference(looked_at))}")
