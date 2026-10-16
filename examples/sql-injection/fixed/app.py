"""Parameter binding keeps an owner value separate from SQL syntax."""


def invoices_for(connection, owner):
    return connection.execute(
        "SELECT id, owner, amount FROM invoices WHERE owner = ?", (owner,)
    ).fetchall()
