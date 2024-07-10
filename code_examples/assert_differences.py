import tomllib
from config_utils import diff_configs


def assert_differences(config1, config2, expected_diffs, excludes=None):
    actual_diffs = diff_configs(config1, config2)

    # Loop over expected diffs to try to find a match in actual diffs
    # If the path has the exclude string at the beginning then skip it.
    # If its missing raise an exception.
    for path1, d1, d2 in expected_diffs:
        if excludes and any([exclude in path1 for exclude in excludes]):
            continue
        if path1 not in [x[0] for x in actual_diffs]:
            assert False, "{} is missing from actual differences".format(path1)

        for path2, d3, d4 in actual_diffs:
            if path1 == path2:
                assert d1 == d3, f"{path1} {d1}!={d3}"
                assert d2 == d4, f"{path1} {d2}!={d4}"

    # Do the same in reverse
    for path1, d1, d2 in actual_diffs:
        if excludes and any([exclude in path1 for exclude in excludes]):
            continue
        if path1 not in [x[0] for x in expected_diffs]:
            assert (
                False
            ), "path1 = {}, d1 = {}, d2 = {}, {} is missing from expected differences".format(
                path1, d1, d2, path1
            )

        for path2, d3, d4 in expected_diffs:
            if path1 == path2:
                assert d1 == d3, f"{path1} {d1}!={d3}"
                assert d2 == d4, f"{path1} {d2}!={d4}"


# Just to save having extra files, we'll directly load toml from a string
c1 = tomllib.loads(
    """
[x]
a = 1
b = 2
[x.y]
c = 3
d = 4
"""
)

c2 = tomllib.loads(
    """
[x]
a = 1
b = 3
[x.y]
c = 4
"""
)

assert_differences(
    c1,
    c2,
    [
        ("x.b", 2, 3),
        ("x.y.c", 3, 4),
        ("x.y.d", 4, None),
    ],
)
