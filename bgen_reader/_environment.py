import os
from pathlib import Path

from appdirs import user_cache_dir

from ._file import make_sure_dir_exist

CUSTOM_CACHE = None

BGEN_READER_CACHE_HOME = Path(
    os.environ.get(
        "BGEN_READER_CACHE_HOME",
        default=Path(user_cache_dir("bgen-reader", "limix")) / "bgen-reader",
    )
)


def custom_meta_path(custom_path: Path = None):
    """
    All end user to over-ride default path behaviors and store files in a set
    location. Potentially useful if working on a linux cluster where
    permissions issues are more prevalent.

    :param custom_path: Path to a directory to store meta data
    """
    global CUSTOM_CACHE
    CUSTOM_CACHE = custom_path


__all__ = ["BGEN_READER_CACHE_HOME", "custom_meta_path", "CUSTOM_CACHE"]

make_sure_dir_exist(BGEN_READER_CACHE_HOME)
make_sure_dir_exist(BGEN_READER_CACHE_HOME / "test_data")
make_sure_dir_exist(BGEN_READER_CACHE_HOME / "metafile")
