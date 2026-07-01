"""Refusal calibration eval.

Tests whether models correctly calibrate refusal behavior on closely related
civic-information questions. Uses paired tasks — each pair presents two queries
that use the same public-records research techniques but differ in stated intent:
one is legitimate civic or journalistic research (answer expected), the other is
harassing, retaliatory, or intimidating (refuse expected).

Scorers:

- appropriate_refusal      — primary: every task carries refusal_expected
- rubric_judge             — quality of answer and refusal judgment
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
            appropriate_refusal(),
            rubric_judge(),
        ],
    )
