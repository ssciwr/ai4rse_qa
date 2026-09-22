import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from openevals import create_trajectory_llm_as_judge
from pydantic import SecretStr
from pprint import pprint
from eval_harness.trajectory_parser import TrajectoryParser

# enumerate all the recordings we have.
RECORDINGS = Path(__file__).parents[1] / "sesssion_recordings"
HARNESSES = [
    (RECORDINGS / "pi" / "trace_gptluna.jsonl", "pi"),
    (RECORDINGS / "pi" / "trace_inkling.jsonl", "pi"),
    (RECORDINGS / "claude" / "trace.jsonl", "claude"),
    (RECORDINGS / "codex" / "trace.jsonl", "codex"),
]

# minimum adherence score
MIN_ADHERENCE_SCORE = 0.7


pytestmark = pytest.mark.judge


@pytest.fixture(scope="module")
def llm_judge():
    env_file = os.getenv("WORKFLOW_JUDGE_ENV_FILE")
    if env_file is None:
        pytest.skip("judge tests are run manually; WORKFLOW_JUDGE_ENV_FILE not set")

    env_path = Path(env_file).expanduser()
    if not env_path.is_file():
        raise ValueError(f"Judge env file does not exist: {env_path}")

    cfg = dotenv_values(env_path)  # dict only, os.environ untouched
    missing = [k for k in ("PROVIDER", "API_KEY", "MODEL") if not cfg.get(k)]
    if missing:
        raise ValueError(f"Missing in judge env file: {', '.join(missing)}")

    api_key = SecretStr(cfg["API_KEY"])
    model_name = cfg["MODEL"]
    provider = cfg["PROVIDER"].lower()

    if provider == "openai":
        return ChatOpenAI(api_key=api_key, model=model_name, temperature=0)
    if provider == "anthropic":
        return ChatAnthropic(
            api_key=api_key,
            model_name=model_name,
            temperature=0,
            timeout=None,
            stop=None,
        )
    if provider == "other":
        url = cfg.get("URL")
        if not url:
            raise ValueError("URL must be given in judge env file for provider 'other'")
        return ChatOpenAI(
            base_url=url, api_key=api_key, model=model_name, temperature=0
        )

    raise ValueError(f"Unknown provider: {provider}")


# get the skill's text. We need this for the judge to grade the session traces
# we do this only once per test session
@pytest.fixture(scope="session")
def skill():
    return (Path(__file__).parents[1] / "skills" / "bugfixing" / "SKILL.md").read_text(
        encoding="utf-8"
    )


@pytest.fixture
def judge_prompt_plan():
    prompt = """
You are an expert evaluator assessing whether an AI agent followed its declared plan during execution.
Your task is to determine whether the agent's actions align with its stated plan.

<Rubric>
Plan adherence means:
- All planned steps are executed in the trace
- Steps are performed in the same order as the plan
- No additional major actions beyond what was planned
- Each step is clearly verifiable in the execution

Plan non-adherence includes:
- Missing or skipped steps from the plan
- Steps executed in a different order than planned
- Extra actions or tool calls not mentioned in the plan
- Ambiguous trace entries that don't clearly match plan steps
- Partial or incomplete execution of planned steps
</Rubric>

<Instructions>
For the execution trace:
- Read the agent's plan carefully
- Review the execution to find corresponding actions for each step
- Verify that each planned step appears in the trace
- Check that steps are executed in the same order as planned
- Identify any actions in the trace not present or unclear in the plan
- Make a final judgement on whether the agent followed the plan and output a score
</Instructions>

<Reminder>
You are evaluating plan obedience only, not whether the agent succeeded at the task or produced correct results.
A successful outcome with plan deviations receives a low score.
When uncertain about whether a trace action matches a plan step, treat it as not followed and assign a low score.
</Reminder>

Now, please grade the following example according to the above instructions:

<example>
<input>
{inputs}
</input>

<plan>
{plan}
</plan>

<output>
{outputs}
</output>
</example>
"""

    return prompt


@pytest.fixture
def judge_prompt_trajectory():
    prompt = """You are an expert data labeler. Your task is to grade the accuracy of an AI agent's tool selection during the resolution of a user query.

<Rubric>
Accurate tool selection:
- Uses the most appropriate tool for each step given the context
- Avoids unnecessary or redundant tool calls
- Uses tools in a logical order where dependencies exist
- Is semantically equivalent to the provided reference tool sequence, if present
</Rubric>

<Instructions>
1. Grade the following thread, evaluating whether the agent selected the right tools in the right order to resolve the user's query efficiently.
2. Evaluate both the choice of tools and whether any tools were unnecessary, missing, or could have been replaced with a more appropriate alternative
</Instructions>

Please grade the following trajectory according to the above instructions:

<trajectory>
{outputs}
</trajectory>
"""
    return prompt


@pytest.mark.parametrize("path,harness", HARNESSES)
def test_workflow_score_plan_adherence(
    llm_judge, path, harness, skill, judge_prompt_plan
):

    #  we need to parse the trace into the openai-messages format
    # that openevals wants
    messages = TrajectoryParser().parse(path, harness=harness)
    # the human's bug report, not injected AGENTS.md or skill text
    task = next(
        m["content"]
        for m in messages
        if m["role"] == "user" and "bug ticket" in m["content"]
    )

    evaluator = create_trajectory_llm_as_judge(
        judge=llm_judge,
        prompt=judge_prompt_plan,
        feedback_key="skill_adherence",
        continuous=True,
    )
    result = evaluator(outputs=messages, inputs=task, plan=skill)

    assert isinstance(result, dict)
    pprint(result)
    assert result["score"] >= MIN_ADHERENCE_SCORE, result["comment"]


@pytest.mark.parametrize("path,harness", HARNESSES)
def test_workflow_score_trajectory_quality(
    llm_judge, path, harness, skill, judge_prompt_trajectory
):

    #  we need to parse the trace into the openai-messages format
    # that openevals wants
    messages = TrajectoryParser().parse(path, harness=harness)
    # the human's bug report, not injected AGENTS.md or skill text
    task = next(
        m["content"]
        for m in messages
        if m["role"] == "user" and "bug ticket" in m["content"]
    )

    evaluator = create_trajectory_llm_as_judge(
        judge=llm_judge,
        prompt=judge_prompt_trajectory,
        feedback_key="skill_adherence",
        continuous=True,
    )

    result = evaluator(outputs=messages, inputs=task, plan=skill)

    assert isinstance(result, dict)
    pprint(result)
    assert result["score"] >= MIN_ADHERENCE_SCORE, result["comment"]
