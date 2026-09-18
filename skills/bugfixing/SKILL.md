---
name: bugfixing
description: >
  Bugfix workflow. Use when the user asks to fix a defect with evidence, tests, a plan approval gate, and reviewer critique before handoff.
---

# Bugfixing

Run a gated bugfix: prove the bug is red, find the culprit code, write an evidence-backed patch plan, wait for approval, implement, then review-loop until the handoff is clean enough.

## Workflow

1. Prove red.
   - Reproduce the reported failure or demonstrate the incorrect behavior with a command, test, log, trace, or code-path observation.
   - Add a regression test that demonstrates the failure
   - If red cannot be reproduced, stop and report the attempted commands, observed results, and missing information needed from the human.
   - Completion criterion: the current state is shown wrong by concrete evidence, or non-reproduction is documented with the evidence attempted.

2. Find the culprit.
   - Trace from the red behavior to the responsible code path.
   - Separate culprit code from callers, fixtures, mocks, generated files, and unrelated symptoms.
   - Completion criterion: every claimed culprit location has file paths, symbols, and evidence linking it to red.

3. Write the patch plan.
   - Before changing production code, write `bugfix-plan.md` unless the user or repository conventions require another path.
   - Include:
     - problem statement;
     - red evidence and commands;
     - culprit code and why it is wrong;
     - minimally invasive fix;
     - tests to add or update;
     - evidence that will prove the fix;
     - risks, assumptions, and rollback notes.
   - Completion criterion: the plan file exists and lets another developer judge the fix without rerunning the whole investigation.

4. Wait at the approval gate.
   - Ask the human to approve, reject, or modify the patch plan.
   - Implement only after explicit approval, unless the user has already authorized implementation without plan review.
   - Completion criterion: the human has approved the plan or given revised direction.

5. Implement the approved patch.
   - Make the smallest change that satisfies the approved plan.
   - Add or update the planned tests first when practical; otherwise record why not.
   - Run the focused failing tests and relevant regression checks.
   - Completion criterion: the approved patch is implemented and test/evidence results are recorded.

6. Run a focused critique.
   - Use a critical reviewer agent when available; otherwise perform a labelled self-review.
   - Ask for a defect list on the bugfix diff only, checking correctness, regression coverage, minimality, edge cases, error handling, and support for claims.
   - Classify each defect as blocker, high, medium, low, or informational.
   - Completion criterion: a classified defect list exists.

7. Review-loop up to four times.
   - Fix blocker, high, and medium defects unless the human explicitly accepts the risk.
   - Leave low-impact issues only when they do not threaten correctness, data loss, security, public API compatibility, or maintainability of touched code.
   - After each correction, rerun relevant tests and request another focused critique.
   - Stop when the defect list is clean, only low-impact issues remain, or four critique/correction cycles have completed.
   - Completion criterion: the remaining defect list is clean or low-impact only, or higher-impact defects after four cycles are explicitly escalated.

8. Hand off for final approval.
   - Report files changed, commands run with results, defects found and fixed during critique, remaining issues with impact and rationale, and any approval decisions needed.
   - Completion criterion: the human receives a final approval request listing fixed issues and remaining issues.

## Rules

- Minimality: prefer the narrowest change that corrects the verified defect.
- Evidence: every diagnosis, fix claim, and remaining risk points to a test, command, trace, code path, or reviewer finding.
- Done means the defect list is clean or only low-impact issues remain; higher-impact defects require explicit human acceptance.
