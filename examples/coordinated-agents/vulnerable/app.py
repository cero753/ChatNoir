"""Intentionally vulnerable synthetic quorum. Never deploy."""


def run_consensus(messages, executor):
    proposal = messages[0]["proposal"]
    approvers = {m["sender"] for m in messages
                 if m["task_id"] == "synthetic-task-001"
                 and m["approved"] is True and m["proposal"] == proposal}
    if len(approvers) < 2:
        raise PermissionError("Two peer approvals required")
    # Peer agreement is wrongly treated as authority from the original user.
    return executor.execute_action(proposal)
