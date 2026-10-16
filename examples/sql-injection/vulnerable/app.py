"""Intentionally vulnerable teaching fixture. Synthetic local data only."""


def invoices_for(connection, owner):
    return connection.execute(
        f"SELECT id, owner, amount FROM invoices WHERE owner = '{owner}'"
    ).fetchall()
