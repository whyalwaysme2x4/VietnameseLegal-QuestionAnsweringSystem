"""Resolve exact historical input bytes without rewriting saved evidence."""
import hashlib
import json
from pathlib import Path


def resolve_artifact(root, week, path, digest):
    root=Path(root).resolve()
    live=(root/path).resolve()
    if not live.is_relative_to(root):
        raise ValueError('Artifact path outside repository')
    if live.is_file() and hashlib.sha256(live.read_bytes()).hexdigest()==digest:
        return live
    index=root/'Evidence/_history/index.json'
    if week in {f'W{i:02d}' for i in range(1,8)} and index.is_file():
        entries=json.loads(index.read_text(encoding='utf-8'))['entries']
        for entry in entries:
            if (entry['week'],entry['path'],entry['sha256'])!=(week,path,digest):
                continue
            snapshot=(root/entry['snapshot_path']).resolve()
            if (snapshot.is_relative_to((root/'Evidence/_history').resolve()) and snapshot.is_file()
                    and hashlib.sha256(snapshot.read_bytes()).hexdigest()==digest):
                return snapshot
    # Keep a failed/missing artifact visible to the caller, never skip validation.
    return live
