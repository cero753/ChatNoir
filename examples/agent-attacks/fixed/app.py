"""Fixed synthetic boundaries; authorization comes from the receiving executor."""
import json


def run_prompt(retrieved_text, model, executor):
    messages = [{"role": "system", "content": "Summarize the supplied document."}]
    messages.append({"role": "user", "content": retrieved_text})
    action = executor.authorize(model(messages))
    return executor.execute_action(action)


def run_tool_output(tool_output, executor):
    action = executor.authorize(json.loads(tool_output))
    return executor.execute_action(action)


def run_peer_message(message, executor):
    # A peer's claimed sender, capabilities and rationale cannot grant authority.
    action = executor.authorize(message["proposal"])
    return executor.execute_action(action)
