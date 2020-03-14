from threading import RLock

import dask.dataframe as dd
from cachetools import LRUCache, cached
from dask.delayed import delayed
from pandas import DataFrame

from ._bgen import bgen_file, bgen_metafile
from ._ffi import ffi, lib
from ._string import create_string


def create_variants(nvariants: int, metafile_filepath):

    with bgen_metafile(metafile_filepath) as mf:
        npartitions = lib.bgen_metafile_npartitions(mf)

    dfs = []
    index_base = 0
    part_size = _get_partition_size(nvariants, npartitions)
    divisions = []
    for i in range(npartitions):
        divisions.append(index_base)
        d = delayed(read_partition)(metafile_filepath, i, index_base)
        dfs.append(d)
        index_base += part_size
    divisions.append(nvariants - 1)
    meta = [
        ("id", str),
        ("rsid", str),
        ("chrom", str),
        ("pos", int),
        ("nalleles", int),
        ("allele_ids", str),
        ("vaddr", int),
    ]
    df = dd.from_delayed(dfs, meta=dd.utils.make_meta(meta), divisions=divisions)
    return df


cache = LRUCache(maxsize=3)
lock = RLock()


@cached(cache, lock=lock)
def read_partition(metafile_filepath, part, index_base):
    with bgen_metafile(metafile_filepath) as mf:

        metadata = lib.bgen_metafile_read_partition(mf, part)
        if metadata == ffi.NULL:
            raise RuntimeError(f"Could not read partition {part}.")

        nvariants = lib.bgen_metafile_nvariants(mf)
        variants = []
        for i in range(nvariants):
            variant = lib.bgen_partition_get_variant(metadata, i)
            id_ = create_string(variant[0].id)
            rsid = create_string(variant[0].rsid)
            chrom = create_string(variant[0].chrom)
            pos = variant[0].position
            nalleles = variant[0].nalleles
            allele_ids = _read_allele_ids(variant[0].allele_ids, variant[0].nalleles)
            vaddr = variant[0].genotype_offset
            variants.append([id_, rsid, chrom, pos, nalleles, allele_ids, vaddr])

        index = range(index_base, index_base + nvariants)
        variants = DataFrame(
            variants,
            index=index,
            columns=["id", "rsid", "chrom", "pos", "nalleles", "allele_ids", "vaddr"],
            dtype=str,
        )
        variants["pos"] = variants["pos"].astype("uint32")
        variants["nalleles"] = variants["nalleles"].astype("uint16")
        variants["vaddr"] = variants["vaddr"].astype("uint64")

    return variants


def _get_partition_size(nvariants: int, npartitions: int):
    return _ceildiv(nvariants, npartitions)


def _ceildiv(a, b):
    return -(-a // b)


def _read_allele_ids(allele_ids, nalleles):
    alleles = [create_string(allele_ids[i]) for i in range(nalleles)]
    return ",".join(alleles)
