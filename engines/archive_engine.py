import os
import zipfile
import tarfile
import hashlib
import subprocess
import platform
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable
import threading


@dataclass
class ArchiveOptions:
    source: str = ""
    output: str = ""
    format: str = "zip"
    compression_level: int = 6
    password: str = ""
    split_size: int = 0
    include_hidden: bool = False
    exclude_patterns: list = field(default_factory=list)
    solid: bool = True
    threads: int = 4
    volume_size: int = 0
    on_progress: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None


class ArchiveEngine:
    FORMATS = ['zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', '7z', 'iso']

    def __init__(self):
        self._stop_event = threading.Event()
        self._running = False
        self._cancelled = False

    def stop(self):
        self._stop_event.set()
        self._cancelled = True

    def _get_total_size(self, path: str) -> int:
        total = 0
        if os.path.isfile(path):
            return os.path.getsize(path)
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total

    def _get_file_count(self, path: str) -> int:
        count = 0
        if os.path.isfile(path):
            return 1
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count

    def _create_zip(self, options: ArchiveOptions):
        compress_level = min(max(options.compression_level, 0), 9)
        compress_type = zipfile.ZIP_DEFLATED if compress_level > 0 else zipfile.ZIP_STORED

        pwd_bytes = options.password.encode('utf-8') if options.password else None

        with zipfile.ZipFile(options.output, 'w', compression=compress_type,
                              compresslevel=compress_level if compress_level > 0 else None) as zf:
            files = []
            if os.path.isfile(options.source):
                files = [options.source]
            else:
                for root, dirs, fnames in os.walk(options.source):
                    for fname in fnames:
                        files.append(os.path.join(root, fname))

            total = len(files)
            for i, fpath in enumerate(files):
                if self._stop_event.is_set():
                    return

                arcname = os.path.relpath(fpath, os.path.dirname(options.source) if os.path.isdir(options.source) else '.')
                if pwd_bytes:
                    zf.writestr(arcname, open(fpath, 'rb').read(), pwd_type=zipfile.WZ_AES)
                else:
                    zf.write(fpath, arcname)

                if options.on_progress:
                    options.on_progress(i + 1, total, fpath)

    def _create_tar(self, options: ArchiveOptions):
        mode_map = {
            'tar': 'w',
            'tar.gz': 'w:gz',
            'tar.bz2': 'w:bz2',
            'tar.xz': 'w:xz',
        }
        mode = mode_map.get(options.format, 'w')
        compresslevel = options.compression_level if options.format != 'tar' else None

        with tarfile.open(options.output, mode, compresslevel=compresslevel) as tf:
            files = []
            if os.path.isfile(options.source):
                files = [options.source]
            else:
                for root, dirs, fnames in os.walk(options.source):
                    for fname in fnames:
                        files.append(os.path.join(root, fname))

            total = len(files)
            for i, fpath in enumerate(files):
                if self._stop_event.is_set():
                    return
                arcname = os.path.relpath(fpath, os.path.dirname(options.source) if os.path.isdir(options.source) else '.')
                tf.add(fpath, arcname=arcname)
                if options.on_progress:
                    options.on_progress(i + 1, total, fpath)

    def _create_7z(self, options: ArchiveOptions):
        cmd = ['7z', 'a']
        if options.compression_level:
            cmd.append(f'-mx={min(options.compression_level, 9)}')
        if options.password:
            cmd.append(f'-p{options.password}')
            cmd.append('-mhe=on')
        if options.threads > 1:
            cmd.append(f'-mmt={options.threads}')
        if options.split_size > 0:
            size_mb = options.split_size // (1024 * 1024)
            cmd.append(f'-v{size_mb}m')
        cmd.append(options.output)
        cmd.append(options.source)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"7z failed: {result.stderr}")

    def _create_iso(self, options: ArchiveOptions):
        cmd = None
        for tool in ['mkisofs', 'genisoimage', 'xorriso']:
            if subprocess.run(['which', tool], capture_output=True).returncode == 0:
                cmd = tool
                break

        if cmd is None:
            raise RuntimeError("No ISO creation tool found. Install genisoimage, mkisofs, or xorriso.")

        iso_cmd = [cmd, '-o', options.output, '-R', '-J', '-V', Path(options.source).name]
        if cmd == 'xorriso':
            iso_cmd = ['xorriso', '-as', 'mkisofs', '-o', options.output, '-R', '-J', options.source]
        else:
            iso_cmd.append(options.source)

        result = subprocess.run(iso_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ISO creation failed: {result.stderr}")

    def execute(self, options: ArchiveOptions) -> bool:
        self._running = True
        self._cancelled = False
        self._stop_event.clear()

        try:
            os.makedirs(os.path.dirname(os.path.abspath(options.output)), exist_ok=True)

            if options.format == 'zip':
                self._create_zip(options)
            elif options.format in ('tar', 'tar.gz', 'tar.bz2', 'tar.xz'):
                self._create_tar(options)
            elif options.format == '7z':
                self._create_7z(options)
            elif options.format == 'iso':
                self._create_iso(options)
            else:
                raise ValueError(f"Unsupported format: {options.format}")

            if self._cancelled:
                return False

            if options.on_complete:
                options.on_complete(options.output, os.path.getsize(options.output))

            return True

        except Exception as e:
            if options.on_error:
                options.on_error(str(options.output), str(e))
            return False
        finally:
            self._running = False

    @staticmethod
    def get_available_formats() -> list:
        formats = ['zip', 'tar', 'tar.gz', 'tar.bz2']
        if subprocess.run(['which', '7z'], capture_output=True).returncode == 0:
            formats.append('7z')
        for tool in ['mkisofs', 'genisoimage', 'xorriso']:
            if subprocess.run(['which', tool], capture_output=True).returncode == 0:
                formats.append('iso')
                break
        return formats

    @staticmethod
    def extract(archive_path: str, dest_path: str) -> bool:
        try:
            os.makedirs(dest_path, exist_ok=True)
            ext = os.path.splitext(archive_path)[1].lower()

            if archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
                with tarfile.open(archive_path, 'r:gz') as tf:
                    tf.extractall(dest_path)
            elif archive_path.endswith('.tar.bz2'):
                with tarfile.open(archive_path, 'r:bz2') as tf:
                    tf.extractall(dest_path)
            elif archive_path.endswith('.tar.xz'):
                with tarfile.open(archive_path, 'r:xz') as tf:
                    tf.extractall(dest_path)
            elif archive_path.endswith('.tar'):
                with tarfile.open(archive_path, 'r') as tf:
                    tf.extractall(dest_path)
            elif ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(dest_path)
            elif archive_path.endswith('.7z'):
                result = subprocess.run(['7z', 'x', archive_path, f'-o{dest_path}', '-y'],
                                       capture_output=True, text=True)
                return result.returncode == 0
            else:
                return False
            return True
        except Exception:
            return False
