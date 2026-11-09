"""Hidden task-stream registry and generator for the held-out test.

Everything that can regenerate test answers lives in this file: the secret
seeds that define each stream's teacher maps, the label noise, and the held-out
test inputs. It must stay inside ``eval/test/``.

Only the *public* parts of a stream -- the frozen base weight, the per-task
input shifts and the training/validation inputs -- are derived from public
seeds. ``data/streams.py`` mirrors exactly that public derivation, and
``eval/test/export_public.py`` writes the public seeds, training labels,
development-stream validation labels and integrity checksums to
``data/streams/manifest.json``. No test input or test label is ever written to
disk; they are regenerated here at test time.
"""

from __future__ import annotations

import hashlib

import numpy as np

NUM_CLASSES = 20
INPUT_DIM = 96
SHARED_RANK = 4
TRAIN_PER_TASK = 900
VAL_PER_TASK = 500
TEST_PER_TASK = 1000
LABEL_NOISE = 0.15
TEACHER_SCALE = 0.85
BASE_STD = 0.35
SHIFT_STD = 0.35
COEFF_STD = 0.9
SPECIFIC_STD = 0.12

# Public RNG components (mirrored by data/streams.py).
PUB_BASE, PUB_SHIFT, PUB_X_TRAIN, PUB_X_VAL = 0, 1, 2, 3
# Secret RNG components (never mirrored outside eval/test/).
SEC_SUBSPACE, SEC_COEFF, SEC_SPECIFIC = 10, 11, 12
SEC_TRAIN_NOISE, SEC_X_TEST, SEC_TEST_NOISE, SEC_VAL_NOISE = 13, 14, 15, 16

EXPERIMENTS = {
    "continual_6task_stream": {"num_tasks": 6},
    "continual_10task_stream": {"num_tasks": 10},
}

STREAMS = {
    "d06_00": {"experiment": "continual_6task_stream", "role": "dev", "public_seed": 408400064378777101, "secret_seed": 32198206392018100410364674921814630147},
    "d06_01": {"experiment": "continual_6task_stream", "role": "dev", "public_seed": 3009962240911660226, "secret_seed": 302557517679830880802911773665568256730},
    "d10_00": {"experiment": "continual_10task_stream", "role": "dev", "public_seed": 501293004249057761, "secret_seed": 97648919169567391932009701058821188184},
    "t06_00": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 3484425597759528766, "secret_seed": 15938689414551936343481511911895223749},
    "t06_01": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 3847456472496878428, "secret_seed": 40677093279664746687616970761690575373},
    "t06_02": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 1435060256913080630, "secret_seed": 23441582163959118650773239844678533186},
    "t06_03": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 959974145337379103, "secret_seed": 310410958229372790056529429752850860942},
    "t06_04": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 1646063979811814894, "secret_seed": 109910383195457605926349138489240479324},
    "t06_05": {"experiment": "continual_6task_stream", "role": "test", "public_seed": 1385584549693182578, "secret_seed": 164398087809796408480475419393735917102},
    "t10_00": {"experiment": "continual_10task_stream", "role": "test", "public_seed": 1467928546358646011, "secret_seed": 232517443723792072725828757948087510742},
    "t10_01": {"experiment": "continual_10task_stream", "role": "test", "public_seed": 1089982103931265437, "secret_seed": 234324222765152598956229988792323649465},
    "t10_02": {"experiment": "continual_10task_stream", "role": "test", "public_seed": 3012845910325933781, "secret_seed": 240500919961815855100614290067741642234},
    "t10_03": {"experiment": "continual_10task_stream", "role": "test", "public_seed": 2701547853644487611, "secret_seed": 288562441394708449601161625119413035579},
}


def num_tasks(stream_id: str) -> int:
    return EXPERIMENTS[STREAMS[stream_id]["experiment"]]["num_tasks"]


def stream_ids(role: str | None = None, experiment: str | None = None) -> list[str]:
    return sorted(
        sid
        for sid, spec in STREAMS.items()
        if (role is None or spec["role"] == role) and (experiment is None or spec["experiment"] == experiment)
    )


def _rng(seed: int, component: int, task: int = 0) -> np.random.Generator:
    digest = hashlib.sha256(f"{int(seed)}:{int(component)}:{int(task)}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest, "little"))


# ---------------------------------------------------------------- public part
def public_base(public_seed: int) -> np.ndarray:
    return _rng(public_seed, PUB_BASE).normal(0.0, BASE_STD, size=(NUM_CLASSES, INPUT_DIM)).astype(np.float32)


def public_shift(public_seed: int, task: int) -> np.ndarray:
    return _rng(public_seed, PUB_SHIFT, task).normal(0.0, SHIFT_STD, size=(INPUT_DIM,))


def public_inputs(public_seed: int, task: int, component: int, count: int) -> np.ndarray:
    noise = _rng(public_seed, component, task).standard_normal((count, INPUT_DIM))
    return (noise + public_shift(public_seed, task)).astype(np.float32)


# ---------------------------------------------------------------- secret part
def _teachers(secret_seed: int, base: np.ndarray, count: int) -> list[np.ndarray]:
    rng = _rng(secret_seed, SEC_SUBSPACE)
    left = rng.normal(0.0, 1.0, size=(NUM_CLASSES, SHARED_RANK))
    right = rng.normal(0.0, 1.0, size=(SHARED_RANK, INPUT_DIM))
    teachers = []
    for task in range(count):
        coeff = _rng(secret_seed, SEC_COEFF, task).normal(0.0, COEFF_STD, size=(SHARED_RANK, SHARED_RANK))
        specific = _rng(secret_seed, SEC_SPECIFIC, task).normal(0.0, SPECIFIC_STD, size=(NUM_CLASSES, INPUT_DIM))
        teachers.append(base.astype(np.float64) + TEACHER_SCALE * (left @ coeff @ right + specific))
    return teachers


def _labels(x: np.ndarray, teacher: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    logits = x.astype(np.float64) @ teacher.T + LABEL_NOISE * rng.standard_normal((x.shape[0], NUM_CLASSES))
    return logits.argmax(axis=1).astype(np.int64)


def public_and_labels(stream_id: str) -> dict:
    """Public inputs plus training (and dev validation) labels, for export only."""

    spec = STREAMS[stream_id]
    count = num_tasks(stream_id)
    base = public_base(spec["public_seed"])
    teachers = _teachers(spec["secret_seed"], base, count)
    out = {"base": base, "x_train": [], "y_train": [], "x_val": [], "y_val": []}
    for task in range(count):
        x_train = public_inputs(spec["public_seed"], task, PUB_X_TRAIN, TRAIN_PER_TASK)
        out["x_train"].append(x_train)
        out["y_train"].append(_labels(x_train, teachers[task], _rng(spec["secret_seed"], SEC_TRAIN_NOISE, task)))
        if spec["role"] == "dev":
            x_val = public_inputs(spec["public_seed"], task, PUB_X_VAL, VAL_PER_TASK)
            out["x_val"].append(x_val)
            out["y_val"].append(_labels(x_val, teachers[task], _rng(spec["secret_seed"], SEC_VAL_NOISE, task)))
    return out


def test_split(stream_id: str) -> dict:
    """Frozen base weight plus held-out test inputs/labels, regenerated at test time."""

    spec = STREAMS[stream_id]
    count = num_tasks(stream_id)
    base = public_base(spec["public_seed"])
    teachers = _teachers(spec["secret_seed"], base, count)
    x_test, y_test = [], []
    for task in range(count):
        noise = _rng(spec["secret_seed"], SEC_X_TEST, task).standard_normal((TEST_PER_TASK, INPUT_DIM))
        x = (noise + public_shift(spec["public_seed"], task)).astype(np.float32)
        x_test.append(x)
        y_test.append(_labels(x, teachers[task], _rng(spec["secret_seed"], SEC_TEST_NOISE, task)))
    return {"base": base, "x_test": x_test, "y_test": y_test}
