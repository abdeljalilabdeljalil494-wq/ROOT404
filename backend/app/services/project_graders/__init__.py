"""Trusted grader extension boundary. Never imports learner/configured Python paths.

Only reviewed code may populate IMPLEMENTATIONS. A completed Markdown template
is not executable configuration and cannot enable a grader. Original eligibility
remains fail-closed until separately reviewed integration and runtime acceptance.
"""
from dataclasses import dataclass
from typing import Protocol
from app.services.grading_contracts import ORIGINAL_PROJECTS


class GraderUnavailable(ValueError):
    pass


@dataclass(frozen=True)
class SubjectReference:
    project: str
    version: str
    sha256: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    weight: int
    hidden: bool


@dataclass(frozen=True)
class Grade:
    score: int
    passed: int
    total: int


def score_cases(cases: tuple[CaseResult, ...]) -> Grade:
    """Trusted-only reducer. Never accepts a score emitted by a learner.

    Project-specific fail/bonus rules belong to the reviewed adapter, not this
    reducer. Raw hidden names, inputs, expectations and diagnostics stay private.
    """
    if not cases or len({case.case_id for case in cases}) != len(cases):
        raise ValueError('Nonempty uniquely identified cases required')
    if any(type(case.passed) is not bool or type(case.weight) is not int or
           case.weight <= 0 or not case.case_id for case in cases):
        raise ValueError('Invalid trusted case result')
    total = sum(case.weight for case in cases)
    return Grade(sum(case.weight for case in cases if case.passed)*100//total,
                 sum(case.passed for case in cases), len(cases))


class TrustedGrader(Protocol):
    subject: SubjectReference

    def evaluate(self, submission, executor) -> Grade:
        """Run an approved harness through the restricted execution adapter.

        Compiler/runtime outcomes come only from verified host receipts; hidden
        expectations and scoring stay backend-side. Never execute learner code
        in this process, on the host, or via an unrestricted Docker client.
        """
        ...


# Deliberately empty: no authoritative original subject/harness exists yet.
IMPLEMENTATIONS: dict[str, TrustedGrader] = {}


def require_grader(project: str) -> TrustedGrader:
    if project not in ORIGINAL_PROJECTS:
        raise GraderUnavailable('Unknown original project')
    grader = IMPLEMENTATIONS.get(project)
    if grader is None:
        raise GraderUnavailable('Approved subject and trusted harness required')
    return grader
