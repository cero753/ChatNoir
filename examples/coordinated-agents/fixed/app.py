"""Peer agreement cannot expand the receiving task's immutable permissions."""


def run_consensus(messages, executor):
    proposal = messages[0]["proposal"]
    approvers = {m["sender"] for m in messages
                 if m["task_id"] == "synthetic-task-001"
                 and m["approved"] is True and m["proposal"] == proposal}
    if len(approvers) < 2:
        raise PermissionError("Two peer approvals required")
    action = executor.authorize(proposal)
    return executor.execute_action(action)
