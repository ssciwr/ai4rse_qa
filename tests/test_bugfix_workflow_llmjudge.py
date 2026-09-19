import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
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


@pytest.fixture(scope="module")
def llm_judge():
    load_dotenv()
    provider = os.getenv("PROVIDER")
    if provider is None:
        raise ValueError("Error, provider must be given in env file")

    if "API_KEY" not in os.environ:
        raise ValueError("Error, API key must be given in .env file")

    if "MODEL" not in os.environ:
        raise ValueError("Error, MODEL must be given in .env file")

    provider = provider.lower()
    model = None
    if provider == "openai":
        model = ChatOpenAI(
            api_key=SecretStr(os.environ["API_KEY"]),
            model=os.environ["MODEL"],
            temperature=0,
        )

    elif provider == "anthropic":
        model = ChatAnthropic(
            api_key=SecretStr(os.environ["API_KEY"]),
            model_name=os.environ["MODEL"],
            temperature=0,
            timeout=None,
            stop=None,
        )
    elif provider == "other":
        url = os.getenv("URL")

        model = os.environ["MODEL"]

        if url is None or model is None:
            raise ValueError(f"Error, {url} or {model} is None")

        model = ChatOpenAI(
            base_url=url,
            api_key=SecretStr(os.environ["API_KEY"]),
            model=model,
            temperature=0,
        )

    if model == None:
        raise ValueError(f"Error, unknown provider: {provider}")
    return model


# get the skill's text. We need this for the judge to grade the session traces
# we do this only once per test session
@pytest.fixture(scope="session")
def skill():
    return (Path(__file__).parents[1] / "skills" / "bugfixing" / "SKILL.md").read_text(
        encoding="utf-8"
    )


@pytest.fixture
def judge_prompt():
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


@pytest.mark.parametrize("path,harness", HARNESSES)
def test_workflow_score_plan_adherence(llm_judge, path, harness, skill, judge_prompt):

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
        prompt=judge_prompt,
        feedback_key="skill_adherence",
        continuous=True,
    )
    result = evaluator(outputs=messages, inputs=task, plan=skill)

    assert isinstance(result, dict)
    pprint(result)
    assert result["score"] >= MIN_ADHERENCE_SCORE, result["comment"]
