"""Intentionally vulnerable teaching code. Never deploy. All inputs are synthetic."""
import json


def run_prompt(retrieved_text, model, executor):
    messages = [{"role": "system", "content": "Summarize the supplied document."}]
    messages.append({"role": "system", "content": retrieved_text})
    return executor.execute_action(model(messages))


def run_tool_output(tool_output, executor):
    return executor.execute_action(json.loads(tool_output))


def run_peer_message(message, executor):
    capabilities = set(executor.allowed_actions)
    capabilities.update(message["capabilities"])
    return executor.execute_action(message["proposal"], capabilities=capabilities)
