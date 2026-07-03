---
name: Kaggle kernels
description: This skill should be used when pushing, running, or debugging Kaggle notebook/script kernels via the kaggle CLI — especially GPU kernels that depend on utility notebooks (kernel_sources), attach competitions/models, or run vLLM/gpt-oss. Covers the kaggle CLI, kernel-metadata.json, the competition→GPU coupling, utility-output mount paths, and common failure modes.
version: 0.1.0
---

# Kaggle kernels

Operate Kaggle kernels (notebooks/scripts) entirely from the `kaggle` CLI: edit
the `.ipynb`/`.py` directly, set `kernel-metadata.json`, push, then poll status
and read logs. The hard part is not the CLI — it is the implicit coupling
between competition sources, the runtime GPU, internet access, and how a
dependency kernel's output gets mounted. Those are documented below because they
are non-obvious and cost real iterations.

Run the CLI with `uv run kaggle ...` (this repo). It prints an "outdated kaggle
version" warning to stderr on every call — ignore it.

**Pushing without asking.** Do **not** ask for permission to push a **CPU**
notebook (any), or a **GPU** notebook expected to run in **under 30 minutes**
(push it with `--timeout 1800`). Just push, poll to terminal, and report the
result — don't offer "want me to push?" for these. Only pause to confirm for
long/expensive GPU runs (>30 min). (Git is separate: the user pushes git commits
themselves — never `git push`.)

**Stopping running sessions without asking.** You are **allowed to stop /
supersede a running kernel session** without asking — especially ones **started
recently** (which have produced no results yet), e.g. to apply a fix and re-run,
or to free one of the 2 concurrent-GPU slots. The CLI has **no dedicated cancel
command** (`kernels` subcommands are list/files/get/init/push/pull/output/status/
logs/update/delete); the stop mechanism is to **`push` the kernel again**, which
cancels its in-flight run and starts the new version. So just re-push the fixed
notebook; the old run is superseded automatically. Prefer letting a short run
that is already near completion finish if its result is still useful.

**Kill slow/wrong/"dead" runs proactively — don't let them burn GPU.** If a run
is clearly going down the wrong path (e.g. mis-tuned config burning compute, or
you've found a fix), **supersede it now** with `push` rather than waiting for it
to finish or time out. The supersede **auto-cancels** the prior in-flight run, so
there is **no separate "zombie" to hunt** — a re-push *is* the kill. There is no
orphaned session left behind. Two corollaries:
- When asked to "kill dead runs", only check the kernels **relevant to the
  current task** (`status huikang/<slug>` for each). Do **not** shotgun-scan
  unrelated kernels in the account — they have nothing to do with the task.
- `status` only ever reflects the **latest** version, so a superseded older
  version won't even show up as running; if the latest is COMPLETE/CANCEL_ACKED,
  that kernel holds no slot.

## CLI essentials

```bash
uv run kaggle kernels push -p <dir> --accelerator NvidiaRtxPro6000  # create new version + run
uv run kaggle kernels status huikang/<slug>     # latest version's run state
uv run kaggle kernels logs   huikang/<slug>      # logs (JSON list); EMPTY while RUNNING
uv run kaggle kernels output huikang/<slug> -p <dir>   # download output files
uv run kaggle kernels files  huikang/<slug>      # list output files (no download)
uv run kaggle kernels pull   huikang/<slug> -p <dir> -m  # pull code + metadata
```

- Every `push` creates a new version **and reruns** the kernel. There is no
  rerun-free way to change settings (privacy, accelerator, sources) — you must
  re-push. A new push **supersedes/cancels** any in-flight run of that kernel.
- `status` / `logs` / `output` always refer to the **latest** version (no
  version flag in CLI 2.1.2).
- `logs` returns only the warning line (no data) while a kernel is RUNNING.
  Logs/outputs appear once the run is terminal. Poll `status` to detect
  COMPLETE / ERROR / CANCEL_ACKED (see the polling snippet at the bottom).
- A metadata-only change (e.g. invalid combo) is rejected at push with
  `400 Client Error ... SaveKernel` — that is a **metadata validation** error,
  not a GPU/quota error, and does not consume a run.

## kernel-metadata.json

```json
{
  "id": "huikang/<slug>",
  "code_file": "<name>.ipynb",     // or a .py for kernel_type "script"
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": false,
  "keywords": [],                    // ["utility script"] makes it a library kernel
  "dataset_sources": [],
  "kernel_sources": ["huikang/pip-install-arc3"],
  "competition_sources": ["arc-prize-2026-arc-agi-3"],
  "model_sources": ["danielhanchen/gpt-oss-120b/Transformers/default/1"],
  "machine_shape": "NvidiaRtxPro6000"
}
```

The `.ipynb` is the artifact you push — **edit it directly** (use the
NotebookEdit tool; for plain `.py` script kernels just edit the file). Do NOT
add a `build_notebook.py`-style generator; it only adds escaping pain (e.g.
`\boxed` must become `\\boxed` through the extra string layer). `model_sources`
entries are `owner/model/Framework/variation/version` (e.g.
`danielhanchen/gpt-oss-120b/Transformers/default/1`); they mount at
`/kaggle/input/<...>` (search for `config.json`).

## The competition source determines the runtime GPU (most important)

`--accelerator NvidiaRtxPro6000` / `machine_shape` is a *request*, not a
guarantee. What actually decides the GPU is the **competition source**:

- A code competition supplies its own runtime environment. `arc-prize-2026-arc-agi-3`
  runs on the **RTX Pro 6000** (Blackwell, 96 GB); `ai-mathematical-olympiad-progress-prize-3`
  runs on an **H100** (80 GB).
- Attach **exactly one** competition matching the GPU you want. Attaching
  **two** competitions (e.g. arc3 + aimo3) makes Kaggle unable to reconcile the
  environments and it silently **falls back to a Tesla P100** (16 GB).
- A kernel with **no** competition source also gets the default P100.

So a P100 fallback despite `--accelerator NvidiaRtxPro6000` almost always means
"wrong/competing competition sources", **not** "RTX unavailable". Fix it by
attaching only the right competition — do not burn runs retrying for GPU
"availability". If a kernel needs data from competition B but the GPU of
competition A, attach only A and **embed the data** (e.g. paste the problem
text into the notebook) instead of attaching B.

A ~16 GB P100 cannot run gpt-oss-120b (~63 GB) and is not even torch-compatible
with the cu128 wheels (sm_60 < sm_70). Assert the GPU early and reject fallbacks:

```python
dn = torch.cuda.get_device_name(0).upper()
assert ("RTX" in dn and "6000" in dn) or "H100" in dn, dn
```

## Internet vs competitions

Code competitions (e.g. arc3) **force `enable_internet: false`**. A kernel that
must `pip install` from the network therefore **cannot** also declare that
competition as a source — Kaggle returns 400. Keep wheel-builder/utility kernels
internet-on with **no** competition source; keep the GPU consumer offline with
the competition source.

## Utility output (kernel_sources) — mount path

A dependency kernel listed in `kernel_sources` has its `/kaggle/working` output
mounted into the consumer. The path varies:

- Current layout: `/kaggle/input/notebooks/<owner>/<slug>/<file>` (e.g.
  `/kaggle/input/notebooks/huikang/pip-install-arc3/arc3_vllm_site`).
- Older / some kernels: `/kaggle/input/<slug>/...`.
- A `["utility script"]` kernel mounts at `/kaggle/usr/lib/<underscored_slug>/`.

Discover robustly with a bounded glob rather than a hard-coded path:

```python
for base in (Path("/kaggle/input/notebooks"), Path("/kaggle/usr/lib"), Path("/kaggle/input")):
    for pat in (sub, f"*/{sub}", f"*/*/{sub}", f"*/*/*/{sub}"):
        for m in sorted(base.glob(pat)):
            if m.is_dir(): return m
```

Also print `sorted(Path('/kaggle/input').iterdir())` early so a missing mount is
diagnosable from the logs.

Note: a `["utility script"]` kernel **cannot** also declare a `competition_sources`
(400). So you can have utility-script mounting OR a competition source, not both
— a plain notebook kernel_source mounts fine under `/kaggle/input/notebooks/...`
without the keyword, so prefer that when you also need a competition.

## Dataset (dataset_sources) — mount path

A `dataset_sources` entry like `huikang/arc-agi-3-replays` does **not** reliably
mount at `/kaggle/input/<slug>/`. Confirmed 2026-06-19: it mounted at
`/kaggle/input/datasets/<owner>/<slug>/` (i.e.
`/kaggle/input/datasets/huikang/arc-agi-3-replays/...`). Same lesson as
kernel_sources: never hard-code the path. Glob for the file you want under
`/kaggle/input` recursively (`/kaggle/input/**/<relpath>`) and, on miss, print the
`/kaggle/input` tree so the real mount is diagnosable from the logs. See
`utilities/arc-agi-3-test-simulator` for a working finder.

## Running vLLM / gpt-oss on Kaggle

- Package deps in an internet-on builder kernel (e.g. `pip-install-arc3`) to a
  `--target=` dir; consumers add it to `sys.path`. Two stacks are confirmed
  working on Kaggle's RTX Pro 6000: `vllm[flashinfer]==0.11.2` (torch 2.9/cu128),
  and **`vllm[flashinfer]==0.19.1`** (latest as of Apr 2026 — resolves to **torch
  2.10.0+cu128**, matching the runtime driver; ~3-8% faster single-thread gpt-oss
  decode, more at long ctx). 0.19.1 needs two extra fixes (next two bullets).
- **Pin the web stack or the OpenAI server 500s on every route — true for BOTH
  0.11.2 and 0.19.1.** A bare `--upgrade` pulls `starlette 1.3.1` +
  `prometheus-fastapi-instrumentator 8.0.0` (+ `fastapi 0.137`), which are mutually
  broken (`'_IncludedRouter' object has no attribute 'path'`) → `/v1/models` and
  every other route return 500, so the server looks "up" but is unusable. vLLM
  only floors these (`fastapi>=0.115`, `starlette>=0.46`,
  `prometheus-fastapi-instrumentator>=7.0`, `uvicorn>=0.12`), so pin the known-good
  within-freeze set (satisfies both 0.11.2 and 0.19.1 floors, predates the
  `_IncludedRouter` wrapper):
  `starlette==0.50.0 fastapi==0.121.3 prometheus-fastapi-instrumentator==7.1.0 uvicorn==0.38.0`.
- **vLLM 0.19.1 / torch 2.10 only: the bundled ptxas can't exec from the
  read-only mount.** torch.compile/inductor execs
  `arc3_vllm_site/triton/backends/nvidia/bin/ptxas-blackwell`, but the
  `/kaggle/input/...` kernel_source mount is read-only/noexec →
  `torch._inductor.exc.InductorError: PermissionError [Errno 13] ... ptxas-blackwell`
  and the server dies during startup. Fix in the consumer: copy `site_dir/triton`
  to a writable dir (`/kaggle/working/_exec_libs/triton`), `chmod +x` its files,
  and put that dir FIRST on `sys.path` + `PYTHONPATH` so the runnable copy wins.
  (0.11.2's triton did not exec a separate blackwell ptxas, so it never hit this.)
- **Cap cudagraph capture for low-concurrency work on 0.19.1.** It defaults to
  `FULL_AND_PIECEWISE` capturing ~80 graph sizes up to 1024 (~20 min of GPU per
  server start). For a single-stream solver pass
  `--compilation-config '{"cudagraph_capture_sizes":[1,2,4]}'`; for a benchmark,
  list the batch sizes you actually drive. Decode speed is unchanged; startup
  drops to ~5 min. (A 25-min single-solver deadline will otherwise expire before
  the server is even ready.)
- **TensorFlow collision:** vLLM pulls transformers, which imports TensorFlow at
  import time if present, colliding with Kaggle's preinstalled TF (cuFFT/cuDNN
  "already registered") and crashing the vLLM import. Before importing vLLM:
  `pip uninstall -y tensorflow keras tf-keras` **and** set
  `USE_TF=0`, `USE_FLAX=0`, `USE_TORCH=1` (the real transformers env vars;
  `TRANSFORMERS_NO_TF` is not enough).
- Attention backend by GPU: RTX Pro 6000 (Blackwell) → `VLLM_ATTENTION_BACKEND=TRITON_ATTN`;
  H100 (Hopper) → `FLASH_ATTN` + `VLLM_FLASH_ATTN_VERSION=3`.
- For gpt-oss-120b at 131k context, use `--kv-cache-dtype fp8_e4m3
  --async-scheduling --max-num-batched-tokens 2048 --gpu-memory-utilization 0.95`
  (fits 80 GB H100; comfortable on 96 GB RTX). Drive the python-tool / harmony
  loop client-side via the `/v1/completions` endpoint with
  `extra_body={"return_token_ids": True}` (the chat endpoint drops generated
  token_ids for gpt-oss-120b).

## Polling pattern

To wait on a run, **poll one kernel's `status` until terminal** — do **not**
re-push to "retry" (a push reruns the kernel; it is not a poll). `kaggle kernels
logs -f huikang/<slug>` streams logs once they exist. Run the poll in a
backgrounded shell (a foreground sleep loop is fine there). Distinguish a fast
failure (assert / P100, ~1–2 min) from a real premium-GPU run (model load
~10 min, then the long task):

```bash
prev=""
for i in $(seq 1 150); do
  s=$(uv run kaggle kernels status huikang/<slug> 2>/dev/null | grep -o 'KernelWorkerStatus\.[A-Z_]*')
  [ "$s" != "$prev" ] && { echo "$(date +%H:%M:%S) $s"; prev="$s"; }
  case "$s" in *COMPLETE*|*ERROR*|*CANCEL_ACK*|*FAIL*) echo "TERMINAL $s"; break;; esac
  sleep 45
done
```

Parse logs (a JSON list of `{stream_name,time,data}`) by joining the `data`
fields: `"".join(d["data"] for d in json.loads(raw[raw.find("["):]))`.

## Gotchas checklist

- P100 despite RTX request → check competition sources (one, matching) before
  blaming availability.
- 400 at push → metadata combo invalid (e.g. utility-script + competition, or
  internet-on + offline competition).
- vLLM import crash mentioning tensorflow → uninstall TF + `USE_TF=0`.
- vLLM server "ready" but every `/v1` route 500s (`'_IncludedRouter' ... 'path'`)
  → unpinned `starlette`/`prometheus-fastapi-instrumentator`; pin the within-freeze
  versions (see the vLLM section). The arc3 runtime is package-frozen at
  **2026-06-01**, so `--upgrade` pulling anything newer also risks incompatibility.
- `missing <dir>` from a kernel_source → mount is under `/kaggle/input/notebooks/<owner>/<slug>/`; glob for it.
- Kaggle allows **2 concurrent** batch GPU sessions — run independent GPU
  kernels **in parallel** (e.g. the wheel-builder and the consumer, or two
  experiments) instead of serializing them. A 3rd concurrent push is rejected
  with "Maximum batch GPU session count of 2 reached".
- Don't push to flip a setting on a kernel whose run you want to keep — the push
  cancels it.
