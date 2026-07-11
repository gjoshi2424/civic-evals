"""Legitimate-vs-unacceptable-use refusal calibration eval.

Contrast-pair testing for the refusal boundary on civic-information tasks.
Each pair presents two queries that would use the *same* public-records
research techniques but differ only in the feature that makes the use
legitimate vs. unacceptable: public figure vs. private individual, civic
purpose vs. personal grievance, institutional role vs. idle curiosity. One
side should be answered; the other should be refused or probed.

Measures both failure modes:
- over-refusal — blocking legitimate civic uses (journalism, watchdog
  OSINT, accountability research), the "answer" side scoring 0.0.
- under-refusal — assisting power-concentrating or abusive variants, the
  "refuse" side scoring 0.0.

Persona is deliberately kept OUT of the task rows so the same request can
be re-run across canonical personas as an ablation — the headline question
is whether the refusal boundary itself moves under persona pressure.

Responsive to the EIP x CIP "Checks & Balances" RFP, Pillar A section 2
("distinguish between closely related legitimate and unacceptable uses").

Scorers:

- rubric_judge (primary) — headline is the ``refusal_appropriateness``
  sub-score, not the 3-way mean: this eval is about the refusal boundary,
  so averaging in accuracy/calibrated_uncertainty would dilute the signal
  (a correct refusal has little substantive content to score for accuracy).
  The judge reads each task's law-cited rubric and can credit a probing/
  redirecting response the keyword scorer misses.
- appropriate_refusal (secondary diagnostic) — cheap non-LLM refusal
  marker; every task carries refusal_expected. Kept for cross-eval
  comparability, but its keyword matching is noisy on this eval's
  probe-or-decline behaviour, so it no longer drives the headline.
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import generate

from p3.lib import load_samples
from p3.scorers import appropriate_refusal, rubric_judge

HERE = Path(__file__).parent


@task
def legitimate_use_refusal() -> Task:
    return Task(
        dataset=load_samples(HERE / "tasks.jsonl"),
        solver=generate(),
        scorer=[
            rubric_judge(primary="refusal_appropriateness"),
            appropriate_refusal(),
        ],
    )
