import os
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable
import threading


@dataclass
class SplitOptions:
    source: str = ""
    output_dir: str = ""
    part_size: int = 100 * 1024 * 1024
    prefix: str = "part_"
    create_manifest: bool = True
    on_progress: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None


@dataclass
class MergeOptions:
    source_dir: str = ""
    output_file: str = ""
    manifest_file: str = ""
    verify: bool = True
    on_progress: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None


class SplitEngine:
    def __init__(self):
        self._stop_event = threading.Event()
        self._running = False

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def _file_hash(filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _get_chunk_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def split(self, options: SplitOptions) -> list:
        self._running = True
        self._stop_event.clear()
        parts = []

        try:
            file_size = os.path.getsize(options.source)
            part_size = options.part_size
            num_parts = (file_size + part_size - 1) // part_size
            base_name = os.path.splitext(os.path.basename(options.source))[0]

            with open(options.source, 'rb') as f:
                for i in range(num_parts):
                    if self._stop_event.is_set():
                        break

                    part_name = f"{options.prefix}{base_name}.part{i + 1:04d}"
                    part_path = os.path.join(options.output_dir, part_name)

                    data = f.read(part_size)
                    with open(part_path, 'wb') as part_f:
                        part_f.write(data)

                    chunk_hash = self._get_chunk_hash(data)
                    parts.append({
                        'name': part_name,
                        'path': part_path,
                        'size': len(data),
                        'hash': chunk_hash,
                        'part_number': i + 1,
                    })

                    if options.on_progress:
                        options.on_progress(i + 1, num_parts, part_path)

            if options.create_manifest:
                manifest_path = os.path.join(options.output_dir, f"{base_name}.manifest")
                import json
                manifest = {
                    'original_file': os.path.basename(options.source),
                    'original_size': file_size,
                    'original_hash': self._file_hash(options.source),
                    'part_size': part_size,
                    'total_parts': len(parts),
                    'parts': parts,
                    'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'part_hash_algo': 'sha256',
                }
                with open(manifest_path, 'w') as mf:
                    json.dump(manifest, mf, indent=2)
                parts.append({
                    'name': os.path.basename(manifest_path),
                    'path': manifest_path,
                    'size': os.path.getsize(manifest_path),
                    'hash': self._file_hash(manifest_path),
                    'part_number': 0,
                    'is_manifest': True,
                })

            if options.on_complete:
                options.on_complete(parts)

            return parts

        except Exception as e:
            if options.on_error:
                options.on_error(options.source, str(e))
            return []
        finally:
            self._running = False

    def merge(self, options: MergeOptions) -> bool:
        self._running = True
        self._stop_event.clear()

        try:
            manifest = None
            if options.manifest_file and os.path.exists(options.manifest_file):
                import json
                with open(options.manifest_file, 'r') as mf:
                    manifest = json.load(mf)
            else:
                for f in os.listdir(options.source_dir):
                    if f.endswith('.manifest'):
                        import json
                        with open(os.path.join(options.source_dir, f), 'r') as mf:
                            manifest = json.load(mf)
                        break

            if manifest:
                parts = sorted(manifest['parts'], key=lambda p: p['part_number'])
                part_files = [p['path'] for p in parts if not p.get('is_manifest')]
            else:
                part_files = sorted([
                    os.path.join(options.source_dir, f)
                    for f in os.listdir(options.source_dir)
                    if f.endswith(('.part0001', '.part01')) or (f.startswith('part_') and '.part' in f)
                ])
                if not part_files:
                    all_files = sorted(os.listdir(options.source_dir))
                    part_files = [os.path.join(options.source_dir, f) for f in all_files
                                  if not f.endswith('.manifest')]

            total_parts = len(part_files)
            written = 0

            with open(options.output_file, 'wb') as out_f:
                for i, part_path in enumerate(part_files):
                    if self._stop_event.is_set():
                        return False

                    if not os.path.exists(part_path):
                        raise FileNotFoundError(f"Part file not found: {part_path}")

                    with open(part_path, 'rb') as part_f:
                        data = part_f.read()
                        out_f.write(data)
                        written += len(data)

                    if options.on_progress:
                        options.on_progress(i + 1, total_parts, part_path)

            if options.verify and manifest:
                original_hash = manifest.get('original_hash')
                if original_hash:
                    merged_hash = self._file_hash(options.output_file)
                    if merged_hash != original_hash:
                        raise RuntimeError("Verification failed: merged file hash mismatch")

            if options.on_complete:
                options.on_complete(options.output_file, os.path.getsize(options.output_file))

            return True

        except Exception as e:
            if options.on_error:
                options.on_error(options.source_dir, str(e))
            return False
        finally:
            self._running = False

    @staticmethod
    def find_parts(directory: str, base_name: str = None) -> list:
        parts = []
        for f in sorted(os.listdir(directory)):
            if base_name and base_name not in f:
                continue
            if '.part' in f and not f.endswith('.manifest'):
                parts.append(os.path.join(directory, f))
        return parts
