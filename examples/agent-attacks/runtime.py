"""Deterministic synthetic model and action sink: no network, real secrets or tools."""


class Executor:
    def __init__(self):
        self.allowed_actions = frozenset({"summarize"})
        self.exports = []

    def authorize(self, proposal):
        if (not isinstance(proposal, dict) or set(proposal) != {"action"}
                or not isinstance(proposal["action"], str)
                or proposal["action"] not in self.allowed_actions):
            raise PermissionError("Proposal outside the root task's capabilities")
        return dict(proposal)

    def execute_action(self, proposal, *, capabilities=None):
        # This deliberately permissive sink exposes missing caller authorization.
        # Fixed entrypoints must pass the shared authorize gate before reaching it.
        action = proposal["action"]
        if capabilities is not None and action not in capabilities:
            raise PermissionError("Action not delegated")
        if action == "export_note":
            self.exports.append("SYNTHETIC-NOTE-NOT-A-SECRET")
            return "exported-to-local-list"
        if action == "summarize":
            return "synthetic-summary"
        raise ValueError("Unknown fixture action")


def model(messages):
    """A scripted role-sensitive proposer, NOT an LLM or model-safety benchmark."""
    if any(m["role"] in {"system", "developer"} and "ACTION=export_note" in m["content"]
           for m in messages):
        return {"action": "export_note"}
    return {"action": "summarize"}


def hostile_model(_messages):
    """Even if lower-priority injection succeeds, the fixed action gate must hold."""
    return {"action": "export_note"}
