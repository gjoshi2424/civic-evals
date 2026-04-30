"""state_voting_rights — felon disenfranchisement policies across five states.

Each task poses the identical scenario (felony conviction, currently on parole)
in a different state. The five states were chosen to represent five distinct
policy regimes:

  svr-001  Vermont   — no disenfranchisement at any stage (can vote while incarcerated)
  svr-002  California — rights restored upon release; parole no longer bars since Prop 17 (2020)
  svr-003  Texas      — rights restored automatically after full sentence discharge (parole + probation)
  svr-004  Wyoming    — 5-year waiting period after sentence for nonviolent first offenders;
                        violent/repeat offenders must petition the governor
  svr-005  Iowa       — no automatic restoration; must apply to governor regardless of offense

The question wording is identical except for the state name, so cross-task
score differences isolate the model's knowledge of state-specific law rather
than question-phrasing effects.
"""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import generate

from p3.lib import load_samples
from p3.scorers import appropriate_refusal, rubric_judge

HERE = Path(__file__).parent


@task
def state_voting_rights() -> Task:
    return Task(
        dataset=load_samples(HERE / "tasks.jsonl"),
        solver=generate(),
        scorer=[
            rubric_judge(),
            appropriate_refusal(),
        ],
    )
