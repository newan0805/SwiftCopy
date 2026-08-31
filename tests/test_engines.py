"""Smoke tests for the SwiftCopy engine back-ends (no GUI required)."""
import os
import shutil
import tempfile
import zipfile

import pytest

from engines.copy_engine import CopyOptions, CopyEngine
from engines.archive_engine import ArchiveOptions, ArchiveEngine
from engines.split_engine import SplitOptions, MergeOptions, SplitEngine


@pytest.fixture
def workspace():
    tmp = tempfile.mkdtemp(prefix="swiftcopy_test_")
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_dir(workspace):
    src = os.path.join(workspace, "src")
    os.makedirs(src, exist_ok=True)
    with open(os.path.join(src, "a.txt"), "w") as f:
        f.write("hello world a\n" * 100)
    with open(os.path.join(src, "b.txt"), "w") as f:
        f.write("hello world b\n" * 100)
    return src


def test_copy_file(sample_dir):
    dest = os.path.join(os.path.dirname(sample_dir), "copy")
    opts = CopyOptions(
        source=sample_dir,
        destination=dest,
        verify=True,
        include_parent_folder=False,
    )
    engine = CopyEngine()
    results = engine.execute(opts)
    assert os.path.exists(dest)
    assert os.path.exists(os.path.join(dest, "a.txt"))
    assert os.path.exists(os.path.join(dest, "b.txt"))
    assert results is not None


def test_copy_include_parent_folder(sample_dir):
    dest = os.path.join(os.path.dirname(sample_dir), "copy_parent")
    opts = CopyOptions(
        source=sample_dir,
        destination=dest,
        verify=True,
        include_parent_folder=True,
    )
    engine = CopyEngine()
    engine.execute(opts)
    assert os.path.exists(os.path.join(dest, "src", "a.txt"))


def test_archive_zip_create_and_extract(sample_dir, workspace):
    archive_path = os.path.join(workspace, "out.zip")
    opts = ArchiveOptions(
        source=sample_dir,
        output=archive_path,
        format="zip",
    )
    engine = ArchiveEngine()
    assert engine.execute(opts) is True
    assert os.path.exists(archive_path)
    assert zipfile.is_zipfile(archive_path)

    extract_to = os.path.join(workspace, "extract")
    assert ArchiveEngine.extract(archive_path, extract_to) is True
    assert os.path.exists(os.path.join(extract_to, "src", "a.txt"))
    assert os.path.exists(os.path.join(extract_to, "src", "b.txt"))


def test_split_and_merge(sample_dir, workspace):
    file_to_split = os.path.join(sample_dir, "a.txt")
    parts_dir = os.path.join(workspace, "parts")
    os.makedirs(parts_dir, exist_ok=True)

    engine = SplitEngine()
    parts = engine.split(
        SplitOptions(
            source=file_to_split,
            output_dir=parts_dir,
            part_size=100,
            prefix="part_",
        )
    )
    assert len(parts) >= 2, "file should split into multiple parts"

    merged = os.path.join(workspace, "merged.txt")
    ok = engine.merge(
        MergeOptions(
            source_dir=parts_dir,
            output_file=merged,
            verify=True,
        )
    )
    assert ok is True
    with open(file_to_split, "rb") as f1, open(merged, "rb") as f2:
        assert f1.read() == f2.read()
