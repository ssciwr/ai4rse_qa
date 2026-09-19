"""Normalize coding-agent JSONL recordings for OpenEvals.

Preserve native tool names and inputs; do not infer actions from shell commands.
Session bookkeeping and internal reasoning are excluded from the trajectory.
"""

import json
from pathlib import Path
from typing import Literal


def _text(content: str | list[dict]) -> str:
    """Return text without silently dropping unsupported content.

    Args:
        content: Plain text or a list of harness text blocks.

    Raises:
        ValueError: A block contains something other than supported text.
    """
    if isinstance(content, str):
        return content
    texts = []
    for block in content:
        if block["type"] not in {"text", "input_text", "output_text"}:
            raise ValueError(f"Unsupported text block: {block['type']}")
        texts.append(block["text"])
    return "\n".join(texts)


def _call(call_id: str, name: str, arguments: dict | str) -> dict:
    """Build an OpenAI-style tool call with JSON-string arguments.

    Args:
        call_id: Recorded identifier linking the call to its result.
        name: Native tool name, without aliasing across harnesses.
        arguments: Tool arguments as a dictionary or an existing JSON string.
    """
    if not isinstance(arguments, str):
        arguments = json.dumps(arguments)
    # Validate JSON arguments without changing their contents.
    json.loads(arguments)
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }


def _result(call_id: str, content: str | list[dict]) -> dict:
    """Build a tool-result message linked to its originating call.

    Args:
        call_id: Identifier of the originating tool call.
        content: Recorded output as plain text or text blocks.
    """
    return {"role": "tool", "tool_call_id": call_id, "content": _text(content)}


class TrajectoryParser:
    """Read pi, Claude, or Codex recordings as OpenAI-style messages.

    This test helper converts formats only; it does not evaluate workflow rules
    or reconstruct conversation branches. Records are processed in file order.
    """

    def parse(
        self,
        path: str | Path,
        *,
        harness: Literal["pi", "claude", "codex"],
    ) -> list[dict]:
        """Convert a recording into messages accepted by OpenEvals.

        Args:
            path: UTF-8 JSONL recording, with one object per nonblank line.
            harness: Recording format to use; no format detection is performed.

        Returns:
            Message dictionaries in recorded order, including tool calls/results.

        Raises:
            ValueError: The harness is unknown, or a record is malformed or has
                unsupported message content. Record errors include file and line.
        """
        handlers = {"pi": self._pi, "claude": self._claude, "codex": self._codex}
        if harness not in handlers:
            raise ValueError(f"Unsupported harness: {harness}")
        messages = []
        with open(path, encoding="utf-8") as stream:
            # Unlike str.splitlines(), iteration won't split embedded Unicode
            # line separators that are valid inside JSON strings.
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    messages.extend(handlers[harness](json.loads(line)))
                except (ValueError, KeyError, TypeError) as exc:
                    raise ValueError(f"{path}:{number}: {exc}") from exc
        return messages

    def _blocks(self, message: dict) -> list[dict]:
        """Convert a message, separating embedded tool results from user text.

        Args:
            message: Native message with a role and string or block-list content.
        """
        role = message["role"]
        content = message["content"]
        if isinstance(content, str):
            return [{"role": role, "content": content}]
        messages = []
        pending = {"role": role, "content": ""}
        for block in content:
            kind = block["type"]
            if kind in {"thinking", "redacted_thinking"}:
                continue
            if kind in {"toolCall", "tool_use"}:
                arguments = block["arguments"] if kind == "toolCall" else block["input"]
                pending.setdefault("tool_calls", []).append(
                    _call(block["id"], block["name"], arguments)
                )
            elif kind == "tool_result":
                # Claude puts tool results in user records. Emit them with the
                # tool role, keeping surrounding user text in its original order.
                if pending["content"] or pending.get("tool_calls"):
                    messages.append(pending)
                    pending = {"role": role, "content": ""}
                messages.append(_result(block["tool_use_id"], block.get("content", "")))
            else:
                text = _text([block])
                pending["content"] += ("\n" if pending["content"] else "") + text
        if pending["content"] or pending.get("tool_calls"):
            messages.append(pending)
        return messages

    def _pi(self, record: dict) -> list[dict]:
        """Convert a pi message or omit a session-bookkeeping record.

        Args:
            record: One decoded pi JSONL record.
        """
        if record["type"] != "message":
            return []
        message = record["message"]
        if message["role"] == "toolResult":
            return [_result(message["toolCallId"], message["content"])]
        return self._blocks(message)

    def _claude(self, record: dict) -> list[dict]:
        """Convert a Claude user/assistant record or omit bookkeeping.

        Args:
            record: One decoded Claude JSONL record.
        """
        if record["type"] not in {"user", "assistant"}:
            return []
        return self._blocks(record["message"])

    def _codex(self, record: dict) -> list[dict]:
        """Convert a Codex response item or omit bookkeeping and reasoning.

        Args:
            record: One decoded Codex JSONL record.
        """
        # event_msg repeats actions already represented by response_item.
        if record["type"] != "response_item":
            return []
        item = record["payload"]
        kind = item["type"]
        if kind == "reasoning":
            return []
        if kind == "message":
            return self._blocks(item)
        if kind in {"function_call", "custom_tool_call"}:
            # Custom calls accept free-form source, not JSON arguments. Wrap it
            # as data to preserve it without interpreting or executing it.
            arguments = (
                item["arguments"] if kind == "function_call" else {"input": item["input"]}
            )
            return [{
                "role": "assistant",
                "content": "",
                "tool_calls": [_call(item["call_id"], item["name"], arguments)],
            }]
        if kind in {"function_call_output", "custom_tool_call_output"}:
            return [_result(item["call_id"], item["output"])]
        raise ValueError(f"Unsupported Codex response item: {kind}")
