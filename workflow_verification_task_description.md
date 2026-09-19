# Workflow trajectory verification - Example task

## Overview
This example consists of 2 parts. They don't built on each other, so you can switch between them as you want.

- Deterministic workflow verification based on pre-recorded traces (see sesssion_recordings), which demonstrates how to use the `openevals` library to verify tool calls in a trace. It also is designed to show limits of this approach for complex apps like AI agents.
- An LLM-as-a-judge approach to score success on the recorded trajectories, using the `openevals` library.

## Remarks
- Conceptually, we follow Anthropic's article [Demystifying evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- This branch bundles the buggy app, the workflow to be graded and the grading harness in one project for the purposes of this workshop. In a real world scenario, that might be different.
- We are working with pre-recorded traces here. We could also record them on the fly, but for this workshop we opted to ignore this step and use the json files directly.
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

- For Part 2 (LLM-as-a-judge), you need access to an LLM that acts as the judge. It is configured via a `.env` file in the project root (next to `pyproject.toml`). The file is ignored by git, so your API key stays local.
    - create `.env` with the following variables:
        - `PROVIDER`: one of `openai`, `anthropic` or `other`. Use `other` for any OpenAI-compatible endpoint (SAIA, OpenRouter, Kilo, ...).
        - `API_KEY`: your API key for that provider.
        - `MODEL`: the model id as the provider names it.
        - `URL`: the endpoint's base URL. Only needed for `other`.
    - examples:
        - OpenAI:
            ```
            PROVIDER=openai
            API_KEY=<your openai key>
            MODEL=<openai model id>
            ```
        - Anthropic:
            ```
            PROVIDER=anthropic
            API_KEY=<your anthropic key>
            MODEL=<anthropic model id>
            ```
        - SAIA (GWDG):
            ```
            PROVIDER=other
            URL=https://chat-ai.academiccloud.de/v1
            API_KEY=<your saia key>
            MODEL=<saia model id>
            ```
        - OpenRouter:
            ```
            PROVIDER=other
            URL=https://openrouter.ai/api/v1
            API_KEY=<your openrouter key>
            MODEL=<openrouter model id, e.g. vendor/model>
            ```
        - Kilo Gateway (needs an API key from https://app.kilo.ai, the `/login kilo` of `pi` does not carry over):
            ```
            PROVIDER=other
            URL=https://api.kilo.ai/api/gateway/
            API_KEY=<your kilo key>
            MODEL=<kilo model id>
            ```
    - the judge model must support structured output (JSON schema or tool calling). If a model fails with a response format or tool calling error, try a different one.

- We are using a skill that defines a workflow for bugfixing:
    - reproduce bug
    - add regression test
    - plan out fix and write to file
    - hand over for review
    - implement
    - automated review and correction loop
    - return report
- See: `skills/bugfixing` to read what it does in detail.
- You can install the skill 'bugfixes' for your agent harness (e.g., for project-local skills, copy it to .agents/skills, .claude/skills, .codex/skills), and run it yourself to find get a feel for how it works.

## Steps - Part 1
- We are using the OpenEvals library in this example, and have some prerecorded examples for a saved trajectory of applying the `bugfixing` skill to the bug ticket for claude, codex and pi, with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and inkling (pi only).
- Have a look at the skill in `skills/bugfixing/SKILL.md` to see what the workflow is that it defines.
- read through the issue in `bug_ticket`. The code this talks about is in `src/qa/lotka.py`.
- OPTIONAL: install the skill and apply it to the `bug_ticket` to observer how it works
 with medium thinking level. There is an additional trace for pi with the thinkingmachines/inkling-free model. The example traces have been obtained with the following initial prompt:
"I have a bug ticket in ./bug_ticket. apparently something with the lotka app is wrong. Please use the project local 'bugfixing' skill to fix this problem."
Each trace contains one json object representing one interaction step per line.
- think about the relevant steps in the 'bugfixing' workflow. Which ones are important to verify, which ones could be left out?
- there are three existing test files for trajectory tests:
    - `test_trajectory_reads_bugfixing_skill.py`
    - `test_trajectory_reads_writes_plan.py`
    - `test_trajectory_reads_sourcecode.py`. This one is incomplete.
- fill in the test `test_trajectory_reads_sourcecode` according to the patter in the other two.
- What about the human approval for the plan? how would you implement a test that asserts that this has been part of the workflow at the appropriate step?
- observe what these tests actually establish. What should they establish? What could you do to improve their power? Work with your coding agents through this question, and try to improve the tests or understand alternatives.
- think about the invariants that the `bugfixing` workflow has. How could we test that they are adhered to?

## Steps - Part 2
- We are using the OpenEvals library in this example, and have some prerecorded examples for a saved trajectory of applying the `bugfixing` skill to the bug ticket for claude, codex and pi, with claude sonnet 5 (claude), gpt5.6-Luna (codex, pi) and inkling (pi only).
- Have a look at the skill in `skills/bugfixing/SKILL.md` to see what the workflow is that it defines.
- read through the issue in `bug_ticket`. The code this talks about is in `src/qa/lotka.py`.
- OPTIONAL: install the skill and apply it to the `bug_ticket` to observer how it works
 with medium thinking level. There is an additional trace for pi with the thinkingmachines/inkling-free model. The example traces have been obtained with the following initial prompt:
"I have a bug ticket in ./bug_ticket. apparently something with the lotka app is wrong. Please use the project local 'bugfixing' skill to fix this problem."
Each trace contains one json object representing one interaction step per line.
- consider `tests/test_bugfix_workflow_llmjudge.py`. This implements a simple
llm_as_a_judge test that uses an llm to judge the workflows and grade them between 0.0 and 1.0 on their adherence to the plan as described in the `bugfixing` skill.
configure your .env file and make sure this runs
- play with different models. What changes?
- the given prompt is a copy of openeval's [PLAN_ADHERENCE_PROMPT](https://github.com/langchain-ai/openevals/blob/main/python/openevals/prompts/quality/plan_adherence.py).
Check their content and investigate the judges adherence to it.
- Try to use other prompts that test other things, e.g., [TRAJECTORY_ACCURACY_PROMPT](https://github.com/langchain-ai/openevals/blob/main/python/openevals/prompts/trajectory/accuracy.py)
- Try changing that prompt a bit and observe the effects.


## Questions
- when is deterministic vs LLMs-based evaluation appropriate?
- which inherent LLM properties influence the judge and how could they be mitigated?