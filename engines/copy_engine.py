import os
import sys
import shutil
import hashlib
import subprocess
import platform
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Optional
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class CopyOptions:
    source: str = ""
    destination: str = ""
    recursive: bool = True
    overwrite: bool = True
    verify: bool = True
    preserve_attributes: bool = True
    preserve_symlinks: bool = True
    skip_hidden: bool = False
    skip_system: bool = False
    include_parent_folder: bool = True
    compression: int = 0
    buffer_size: int = 1024 * 1024 * 8
    max_workers: int = 4
    exclude_patterns: list = field(default_factory=list)
    include_patterns: list = field(default_factory=list)
    exclude_extensions: list = field(default_factory=list)
    include_extensions: list = field(default_factory=list)
    min_size: int = 0
    max_size: int = 0
    dry_run: bool = False
    resume: bool = True
    speed_limit: int = 0
    log_file: str = ""
    on_progress: Optional[Callable] = None
    on_file_start: Optional[Callable] = None
    on_file_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None
    on_complete: Optional[Callable] = None


@dataclass
class CopyStats:
    total_files: int = 0
    copied_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    total_bytes: int = 0
    copied_bytes: int = 0
    start_time: float = 0
    errors: list = field(default_factory=list)


class CopyEngine:
    def __init__(self):
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self.stats = CopyStats()
        self.options = CopyOptions()
        self._lock = threading.Lock()
        self._running = False

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    @property
    def is_paused(self):
        return not self._pause_event.is_set()

    @property
    def is_running(self):
        return self._running

    def _should_exclude(self, filepath: str) -> bool:
        name = os.path.basename(filepath)
        if self.options.skip_hidden and name.startswith('.'):
            return True
        if self.options.exclude_patterns:
            from fnmatch import fnmatch
            for pattern in self.options.exclude_patterns:
                if fnmatch(name, pattern):
                    return True
        if self.options.exclude_extensions:
            ext = os.path.splitext(name)[1].lower()
            if ext in self.options.exclude_extensions:
                return True
        return False

    def _should_include(self, filepath: str) -> bool:
        name = os.path.basename(filepath)
        if self.options.include_patterns:
            from fnmatch import fnmatch
            for pattern in self.options.include_patterns:
                if fnmatch(name, pattern):
                    return True
            return False
        if self.options.include_extensions:
            ext = os.path.splitext(name)[1].lower()
            if ext not in self.options.include_extensions:
                return False
        return True

    def _get_file_hash(self, filepath: str, algorithm: str = 'md5') -> str:
        h = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    def _copy_file_native(self, src: str, dst: str) -> bool:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            buf_size = self.options.buffer_size
            total_size = os.path.getsize(src)
            copied = 0

            if self.options.resume and os.path.exists(dst):
                existing_size = os.path.getsize(dst)
                if existing_size == total_size:
                    with self._lock:
                        self.stats.copied_bytes += total_size
                        self.stats.copied_files += 1
                    if self.options.on_file_complete:
                        self.options.on_file_complete(src, dst, True)
                    return True
                elif existing_size < total_size:
                    mode = 'r+b'
                    copied = existing_size
                else:
                    mode = 'wb'
            else:
                mode = 'wb'

            with open(src, 'rb') as fsrc, open(dst, mode) as fdst:
                if copied > 0:
                    fsrc.seek(copied)
                    fdst.seek(copied)

                while copied < total_size:
                    if self._stop_event.is_set():
                        return False
                    self._pause_event.wait()
                    if self._stop_event.is_set():
                        return False

                    remaining = total_size - copied
                    chunk_size = min(buf_size, remaining)
                    data = fsrc.read(chunk_size)
                    if not data:
                        break
                    fdst.write(data)
                    copied += len(data)

                    with self._lock:
                        self.stats.copied_bytes += len(data)

                    if self.options.on_progress:
                        self.options.on_progress(
                            self.stats.copied_bytes,
                            self.stats.total_bytes,
                            src
                        )

                    if self.options.speed_limit > 0:
                        expected_time = copied / (self.options.speed_limit * 1024 * 1024)
                        elapsed = time.time() - self.stats.start_time
                        if elapsed < expected_time:
                            time.sleep(expected_time - elapsed)

            if self.options.preserve_attributes:
                try:
                    shutil.copystat(src, dst, follow_symlinks=self.options.preserve_symlinks)
                except (OSError, PermissionError):
                    pass

            return True

        except Exception as e:
            with self._lock:
                self.stats.errors.append((src, str(e)))
                self.stats.failed_files += 1
            if self.options.on_error:
                self.options.on_error(src, str(e))
            return False

    def _copy_file_system(self, src: str, dst: str) -> bool:
        system = platform.system()
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            if system == 'Windows':
                cmd = ['xcopy', src, dst, '/Y', '/C', '/I', '/H', '/R']
                if self.options.preserve_attributes:
                    cmd.append('/K')
                if self.options.recursive:
                    cmd.append('/E')
                if not self.options.overwrite:
                    cmd = [c for c in cmd if c != '/Y']
                    cmd.append('/-Y')
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode in (0, 1)

            elif system == 'Linux':
                cmd = ['cp', '-f']
                if self.options.preserve_attributes:
                    cmd.append('-p')
                if self.options.recursive:
                    cmd.append('-r')
                if self.options.preserve_symlinks:
                    cmd.append('-d')
                cmd.extend([src, dst])
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0

            elif system == 'Darwin':
                cmd = ['cp']
                if self.options.preserve_attributes:
                    cmd.append('-p')
                if self.options.recursive:
                    cmd.append('-R')
                if self.options.preserve_symlinks:
                    cmd.append('-P')
                cmd.extend([src, dst])
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0

        except Exception as e:
            with self._lock:
                self.stats.errors.append((src, str(e)))
                self.stats.failed_files += 1
            if self.options.on_error:
                self.options.on_error(src, str(e))
            return False
        return False

    def _process_file(self, src: str, dst: str):
        if self._stop_event.is_set():
            return

        if self._should_exclude(src):
            with self._lock:
                self.stats.skipped_files += 1
            return

        if not self._should_include(src):
            with self._lock:
                self.stats.skipped_files += 1
            return

        file_size = os.path.getsize(src)
        if self.options.min_size > 0 and file_size < self.options.min_size:
            with self._lock:
                self.stats.skipped_files += 1
            return
        if self.options.max_size > 0 and file_size > self.options.max_size:
            with self._lock:
                self.stats.skipped_files += 1
            return

        if self.options.on_file_start:
            self.options.on_file_start(src, dst)

        if self.options.dry_run:
            with self._lock:
                self.stats.copied_files += 1
            return

        success = self._copy_file_native(src, dst)

        if success and self.options.verify:
            if not self._stop_event.is_set():
                src_hash = self._get_file_hash(src)
                dst_hash = self._get_file_hash(dst)
                if src_hash != dst_hash:
                    success = False
                    with self._lock:
                        self.stats.errors.append((src, "Verification failed: hash mismatch"))
                        self.stats.failed_files += 1
                    if self.options.on_error:
                        self.options.on_error(src, "Verification failed")

        with self._lock:
            if success:
                self.stats.copied_files += 1
            else:
                self.stats.failed_files += 1

        if self.options.on_file_complete:
            self.options.on_file_complete(src, dst, success)

    def _collect_files(self, src: str) -> list:
        files = []
        if os.path.isfile(src):
            files.append(src)
        elif os.path.isdir(src):
            for root, dirs, filenames in os.walk(src):
                if self.options.skip_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                for fname in filenames:
                    files.append(os.path.join(root, fname))
        return files

    def _resolve_dest_path(self, src_file: str, src_path: Path, dst_path: Path) -> str:
        src_is_dir = src_path.is_dir()
        dst_is_dir = (
            dst_path.is_dir()
            or os.path.basename(str(dst_path)) == ""
            or dst_path.suffix == ""
        )

        if self.options.include_parent_folder and src_is_dir:
            base = dst_path / src_path.name
            rel_path = os.path.relpath(src_file, src_path)
            return str(base / rel_path)

        if src_is_dir:
            rel_path = os.path.relpath(src_file, src_path)
            return str(dst_path / rel_path) if dst_is_dir else str(dst_path)

        rel_path = os.path.basename(src_file)
        return str(dst_path / rel_path) if dst_is_dir else str(dst_path)

    def execute(self, options: CopyOptions):
        self.options = options
        self._stop_event.clear()
        self._pause_event.set()
        self._running = True
        self.stats = CopyStats()

        src_path = Path(options.source)
        dst_path = Path(options.destination)

        if not src_path.exists():
            if self.options.on_error:
                self.options.on_error(str(src_path), "Source does not exist")
            self._running = False
            return self.stats

        files = self._collect_files(str(src_path))
        self.stats.total_files = len(files)
        self.stats.total_bytes = sum(os.path.getsize(f) for f in files if os.path.exists(f))
        self.stats.start_time = time.time()

        if self.options.log_file:
            log_dir = os.path.dirname(options.log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

        for src_file in files:
            if self._stop_event.is_set():
                break

            dst_file = self._resolve_dest_path(src_file, src_path, dst_path)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            self._process_file(src_file, dst_file)

        self._running = False

        if self.options.on_complete:
            self.options.on_complete(self.stats)

        return self.stats

    def get_disk_usage(self, path: str) -> dict:
        try:
            usage = psutil.disk_usage(path) if PSUTIL_AVAILABLE else None
            if usage:
                return {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
        except Exception:
            pass
        return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    def get_system_copy_tool(self) -> str:
        system = platform.system()
        if system == 'Windows':
            return 'xcopy'
        elif system == 'Linux':
            if shutil.which('rsync'):
                return 'rsync'
            return 'cp'
        elif system == 'Darwin':
            return 'cp'
        return 'native'
