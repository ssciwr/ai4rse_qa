# Workflow trajectory verification - Example task

## Overview
This example consists of 2 parts. They don't built on each other, so you can switch between them as you want. However, it makes sense to at least read through the 'Steps' section of part 1 first before you move on to part 2.

Part 1: Deterministic workflow verification based on pre-recorded agent traces (see sesssion_recordings), which demonstrates how to use the `openevals` library to verify tool calls in a trace. It also is designed to work out limits of this approach for complex apps like AI agents.

Part 2: An LLM-as-a-judge approach to score success on the recorded trajectories, using the `openevals` library. This scores the entire trace in one go, but comes with LLM associated drawbacks.

## Remarks
- Security: For step 2, it's recommended you create a dedicated api key for this session or use the saia key you got for this workshop, because we cannot rule out under all circumstances that an API key doesn't land in the agent's context window on accident.
- Conceptually, we follow Anthropic's article [Demystifying evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), but make some compromises for the sake of simplicity.
- This branch bundles the buggy app (/src/qa), the workflow to be graded (/session_recordings) and the grading harness in one project for the purposes of this workshop. In a real world scenario, that might be different.
- We are working with pre-recorded traces here. We could also record them on the fly, but for this workshop we opted to ignore this step and use the record json files directly. See below if you want to record your own.
- We are embedding the tests into pytest here for simplicity, although it often makes sense to use a specialized evaluation harness for that.
- Tool: LangChain OpenEvals. The tool's repository and documentation are here: https://github.com/langchain-ai/openevals . There are many other evaluation libraries out there:
[deepevals](https://deepeval.com/), [pydanitc AI and its evaluator sub-library](https://pydantic.dev/docs/ai/overview/), or the [InspectAI](https://github.com/UKGovernmentBEIS/inspect_ai), among many others.

## Setup
- You need a working python installation.
    - make a virtual environment:
        - raw Python: `python3 -m venv ./.venv`
        - uv: `uv venv ./.venv`
        - PowerShell: `py -m venv .venv`
        - conda: `conda create -n venv`

    - activate the venv
        - raw Python: `source .venv/bin/activate`
        - uv: `source .venv/bin/activate`
        - PowerShell: `.\.venv\Scripts\Activate`
        - conda: `conda activate venv`

    - install the current project in 'editable' mode, together with its dependencies:
        - raw Python: `python -m pip install -e ".[tests]"`
        - uv: `uv sync --extra tests`
        - PowerShell: `python -m pip install -e ".[tests]"`
        - conda: `python -m pip install -e ".[tests]"`

    - how to run tests:
        - raw Python: `python -m pytest`
        - uv: `uv run --extra tests pytest`
        - PowerShell: `python -m pytest`
        - conda: `python -m pytest`

- For Part 2 (LLM-as-a-judge), you need access to an LLM that acts as the judge. Configure it in a `judge.env` file outside the repository. Pass the path to that file through the `WORKFLOW_JUDGE_ENV_FILE` environment variable.
    - The file contains:
        - `PROVIDER`: one of `openai`, `anthropic` or `other`. Use `other` for an OpenAI-compatible endpoint (SAIA, OpenRouter, Kilo, ...).
        - `API_KEY`: your API key for that provider.
        - `MODEL`: the model id as the provider names it.
        - `URL`: the endpoint's base URL. Only needed for `other`.
    - Example:
        ```
        PROVIDER=other
        URL=https://example.com/v1
        API_KEY=<your api key>
        MODEL=<model id>
        ```
    - Create the file with your editor of choice, outside the repository.
    - Run the judge tests manually. Supply the file path only to that command; do not export or persist the variable.
    - Unix/macOS:
        ```bash
        WORKFLOW_JUDGE_ENV_FILE=~/judge.env pytest -m judge
        ```
    - Windows PowerShell:
        ```powershell
        cmd /c 'set "WORKFLOW_JUDGE_ENV_FILE=C:\path\to\judge.env" && python -m pytest -m judge'
        ```
    - The judge model must support structured output (JSON schema or tool calling). If a model fails with a response format or tool calling error, try a different one.

## Goal:
- try out a library for verifying agent trajectories.
- try out a deterministic and an llm-based approach
- find out limits of deterministic verification and llm-based verification

## Background
- We are using a skill that defines a workflow for bugfixing:
    - reproduce bug
    - add regression test
    - plan out fix and write the plan to a file
    - hand the file over for human review and wait for approval
    - implement fix
    - automated review and correction loop: have a reviewer look over fix and hand back remaining issues. Can repeat up to 4 times.
    - return report of what has been done when finished.
- See: `skills/bugfixing` to read what it does in detail.
- You can install the skill 'bugfixes' for your agent harness (e.g., for project-local skills, copy it to .agents/skills, .claude/skills, .codex/skills), and run it yourself to find and fix the bug in the 'lotka' library and get a feel for how it works.
- Four trajectory records of applying this skill to the (buggy) 'lotka' library are provided, so we don't have to deal with building or setting up
a full evaluation harness. One record for claude and codex each, two for pi with different models.
- The example traces have been obtained with the following initial prompt:
"I have a bug ticket in ./bug_ticket. apparently something with the lotka app is wrong. Please use the project local 'bugfixing' skill to fix this problem."
- Each trace contains one json object representing one interaction step per line. They have been obtained with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and inkling (pi only), with medium thinking level each.

## Steps - Part 1
- We are using the OpenEvals library in this example, and have some prerecorded examples for a saved trajectory of applying the `bugfixing` skill to the bug ticket for claude, codex and pi, with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and inkling (pi only).
- Have a look at the skill in `skills/bugfixing/SKILL.md` to see what the workflow is that it defines.
- read through the issue in `bug_ticket`. The code this talks about is in `src/qa/lotka.py`.
- OPTIONAL: install the skill and apply it to the `bug_ticket` to observe how it works (and if).
- think about the relevant steps in the 'bugfixing' workflow. Which ones are important to verify, which ones could be left out? Compare to the two files:
    - `test_trajectory_reads_bugfixing_skill.py`
    - `test_trajectory_reads_sourcecode.py`. This one is incomplete.
- fill in the test `test_trajectory_reads_sourcecode` according to the pattern in `test_trajectory_reads_bugfixing_skill`.
Use your coding agent to work through this if you want. Have it explain what it is planning, why, and what the changes it plans means.
- Make sure you understand what is being verified here with respect to the task.
- What about the human approval gate for the plan? how would you implement a test that asserts that this has been part of the workflow at the appropriate step? How practical is that?
- What should a verification workflow establish?
- What could you do to improve the effectiveness of the current one?
- Think about the invariants of the `bugfixing` workflow. How could we test that they are adhered to?

## Steps - Part 2
- We are using the OpenEvals library for this second step again, but this time with an llm-as-a-judge evaluator.
- some prerecorded examples for a saved trajectory of applying the `bugfixing` skill to the bug ticket for claude, codex and pi, with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and inkling (pi only).
- If not done already: Have a look at the skill in `skills/bugfixing/SKILL.md` to see what the workflow is that it defines.
- If not done already: read through the issue in `bug_ticket`. The code this talks about is in `src/qa/lotka.py`.
- If not done already: OPTIONAL: install the skill and apply it to the `bug_ticket` to observer how it works.
- Configure an external `.env` file and supply `WORKFLOW_JUDGE_ENV_FILE` only to the manual judge-test command as described above.
- Consider `tests/test_bugfix_workflow_llmjudge.py`. This implements a simple
llm_as_a_judge test that uses an llm to judge the workflows and grade them, using a numeric scale, on their adherence to the plan as described in the `bugfixing` skill.
- Play with different models by changing the MODEL entry in your env file. What changes?
- The given prompt is a copy of openeval's [PLAN_ADHERENCE_PROMPT](https://github.com/langchain-ai/openevals/blob/main/python/openevals/prompts/quality/plan_adherence.py). Check the content of the given evaluation prompt and investigate how well the judge adherences to it.
- Try changing that prompt and observe the effects. What parts are missing? Would make a good judge?
- The prompt determines the evaluation, e.g, plan adherence, trajectory efficiency and so on.  Try to use other prompts that test other things, e.g., [TRAJECTORY_ACCURACY_PROMPT](https://github.com/langchain-ai/openevals/blob/main/python/openevals/prompts/trajectory/accuracy.py). Some need a reference trajectory, for which we can use one of the given ones.


## Questions
- When is deterministic vs LLMs-based evaluation appropriate?
- Which inherent LLM properties influence the judge and how could the arising issues be mitigated?
- What perparations are needed to make an LLM-as-a-judge reliable? (We don't have all of them here)