#!/bin/bash
# Fetch / verify every data artifact this gym needs.
#
# Estimated download size: 0 bytes. The benchmark is self-contained: the task
# streams' public inputs are regenerated deterministically from the public
# seeds in data/streams/manifest.json (tracked in git, ~200 KB), and their
# labels are stored in that manifest. Nothing is fetched from the network and
# nothing is read from shared/. This script verifies that every stream can be
# regenerated and matches its stored checksums.
set -e

cd /home/user

python - <<'PY'
from data.streams import load_manifest, load_stream, stream_ids

manifest = load_manifest()
for sid in stream_ids(manifest=manifest):
    stream = load_stream(sid, manifest=manifest)
    print(f"{sid}: {len(stream.tasks)} tasks, role={stream.role}, checksums ok")
PY
