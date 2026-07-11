# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CORDA P3 research project: **Civic Information Reliability** — a shared `inspect-ai` evaluation suite measuring how reliably LLMs answer civic questions across providers, personas, and task types. Each eval lives under `evals/<name>/` and contributes tasks into one uniformly-structured `.eval` log stream; cross-eval rollups operate on that stream, so every eval is directly comparable on accuracy, calibrated uncertainty, appropriate-refusal, consistency, and citation verifiability.

## Commands

Python is managed with `uv`; the site with `pnpm`. A `justfile` wraps the common commands but nothing in CI depends on `just` — the raw commands are authoritative.

```bash
uv sync                                                          # install Python deps (first run)
uv run pytest                                                    # schema validation + scorer fixtures + smoke; no API spend
uv run pytest tests/test_schema.py::test_name                    # single test
uv run ruff check src/ analysis/ tests/                          # lint (just lint)
uv run ruff check --fix src/ analysis/ tests/ && uv run ruff format src/ analysis/ tests/   # just fix

uv run inspect eval evals/voting_access/eval.py --model anthropic/claude-haiku-4-5 --log-dir logs/   # run one eval
uv run inspect view                                              # browse .eval logs — this is how evals are reviewed
uv run python analysis/rollup.py logs/ --format json -o site/public/data/rollup.json   # regenerate rollup (just rollup)
```

`just eval <name> [model] [limit]`, `just eval-all`, `just failures`, `just usage`, `just diff old.json new.json`, `just site` are convenience wrappers. Haiku (`claude-haiku-4-5`) is the default/cheapest model and what CI smoke-runs against.

Site (Next.js App Router, static-exported to GitHub Pages): `cd site && pnpm install && pnpm dev`. It reads `site/public/data/rollup.json` at build time. `pnpm build` (via `just site-build`) catches client/server boundary issues `pnpm dev` tolerates.

## Architecture

The core contract: **an eval is a folder, not a code change to shared infra.** Contributors copy `evals/_template/` and fill in three files — `tasks.jsonl`, `eval.py`, `README.md`. The shared library in `src/p3/` is what makes every eval's output comparable; changing it affects all evals and the rollup.

- **`src/p3/schemas.py`** — the `Task` model every `tasks.jsonl` row must parse as. `load_tasks()` validates on load; empty `metadata.source` and other gaps fail CI (`tests/test_schema*.py`, `tests/test_track.py`).
- **`src/p3/lib/loader.py`** — `load_samples()` bridges on-disk `Task` → inspect-ai `Sample`. Persona preambles are prepended here (never baked into `input`); `refusal_expected` is resolved from `metadata.extras` or legacy `metadata.notes` parsing; metadata propagates so scorers can read per-task flags. Every `eval.py` loads through this.
- **`src/p3/scorers/`** — the shared scorer library. Every scorer returns the standard inspect-ai `Score` shape so the rollup stays scorer-agnostic. Two tiers, enforced via `__init__.py`: `__all__` is production-ready and used by a reference eval; `EXPERIMENTAL` (`consistency_across_paraphrases`, `response_variance`) is importable but not in `__all__` — a PR wiring one into an eval must also add tests for the activated path. **Do not invent new scorers without discussing on the PR** — a bespoke scorer's numbers won't compare to anyone else's in the rollup.
- **`src/p3/providers.py`** — canonical model constants (pinned to dated aliases for measurement reproducibility; see the module docstring's bump policy) and `pick_judge()`, which selects a judge from a *different* provider than the subject to avoid same-model self-bias in rubric scoring. Degrades to a same-provider judge with a warning if the cross-provider key is missing.
- **`src/p3/personas/`** — personas are attribute vectors, not fixed characters. `canonical.py` holds the seven headline personas; reference by name (`{"persona": {"name": "first_time_voter"}}`).
- **`analysis/rollup.py`** — unifies `.eval` logs into one long-form dataframe (`rollup.json` for the site). Reports per-`(eval, provider)` calibration AUROC among other metrics. The many other `analysis/*.py` scripts are one-off experiment/figure generators (persona drift, sycophancy, bias), not part of the eval→rollup→site pipeline.
- **`site/`** — Next.js dashboard reading `rollup.json`. **`tests/`** — CI: schema validation + smoke-runs every eval under Haiku. **`logs/`** — `.eval` outputs, gitignored.

Data flow: `tasks.jsonl` → `load_samples` → inspect-ai `Task`/solver/scorer → `.eval` logs in `logs/` → `analysis/rollup.py` → `rollup.json` → `site/`.

## Task authoring conventions

- Every task needs a real `metadata.source` (URL/statute/named doc); empty strings fail CI.
- Never bake persona into the `input` string — attach it in the persona slot.
- `metadata.track` (`factual` | `interpretive`) is a required CI gate on new tasks. Pick per-*task*, not per-eval. **Do not default to `factual`** — if the answer depends on persona, jurisdiction, or a value judgment, it's `interpretive` (the team's research direction). `voting_access`/`election_integrity`/`fermi_civic_estimation` are factual; `policy_impact_personalization` is interpretive.
- Scorer selection guidance and the LM-Polygraph taxonomy mapping live in `CONTRIBUTING.md`. The scoring layer is intentionally aligned with LM-Polygraph (Vashurin et al., TACL 2025) so results sit alongside published UQ work.
- Refusal expectation goes in `metadata.extras.refusal_expected` (or legacy `metadata.notes: refusal_expected=refuse|answer|hedge`) for `appropriate_refusal()`.
- If using `political_lean` as an ablation dimension, pre-register the hypothesis in the eval's README before running — post-hoc slicing is how cherry-picked findings happen.

See `CONTRIBUTING.md` for the full schema table, scorer table, and pre-PR checklist.
