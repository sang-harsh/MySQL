# Application Integration And Security

[Exercises](21-application-integration-security-exercises.md) | [Topic index](../start.md)

## Interview Answer

An application should send values as bound parameters, keep database privileges limited to what its role needs, and manage connections/transactions explicitly. Prepared statements separate SQL structure from user data and prevent values from becoming executable SQL. I also watch for connection-pool leaks, N+1 query patterns, and unsafe retries when a request's outcome is uncertain.

## Key Points

- Use prepared statements with bound values. Parameters represent values, not table names or SQL keywords; dynamic identifiers need strict allowlists and safe quoting by the database library.
- Do not concatenate untrusted input into SQL. Escaping strings manually is fragile and not a substitute for parameter binding.
- Use separate least-privilege accounts per application/service where practical. Avoid application access with administrative privileges; rotate secrets through approved secret storage.
- Connection pools reuse sessions. Return connections only after commit/rollback and reset session state as the driver requires.
- A transaction must use one connection from START through COMMIT/ROLLBACK. Keep it short and do not hold locks while calling remote services.
- N+1 queries issue one parent query followed by a query per parent. Use a join or batched lookup when appropriate, while preserving the desired row grain and avoiding child-row multiplication.
- MySQL upsert syntax (`INSERT ... ON DUPLICATE KEY UPDATE`) depends on a unique/primary key conflict. It is not a general replacement for checking every business rule.
- Idempotency keys help make retries safe when a network failure leaves a commit outcome unknown. A duplicate request must not repeat a payment or other side effect.

## Minimal Example

```sql
SELECT user_id, display_name
FROM users
WHERE email = ?;
```

The `?` is a parameter marker used through a prepared statement API; the application binds the email as a value. It is not valid to substitute an arbitrary column name through that placeholder.

## Common Traps

- Prepared statements do not make a query safe if untrusted input is still concatenated into another part of it.
- A connection pool does not imply transaction isolation across separate connections; transaction state is session-scoped.
- Fixing N+1 with a join may duplicate parent rows when child cardinality is one-to-many; aggregate or batch with the expected grain.
- An upsert can overwrite data if the duplicate-key update clause is too broad. Keep updates explicit and test unique-key conflicts.
- Do not expose raw database errors or secrets to clients.

## Likely Follow-Ups

**Can a prepared parameter choose a column name?** No; bind parameters represent values. For identifiers, map user choices to a fixed allowlist and construct the statement using the trusted identifier.

**How do you prevent N+1?** Fetch related rows in one join or a bounded batch, then group them in the application. Check the execution plan and output cardinality.

**How do you retry after timeout?** Use a unique idempotency key and check the recorded operation state before repeating side effects.

## MySQL References

Examples target MySQL 8.4. See [PREPARE syntax](https://dev.mysql.com/doc/refman/8.4/en/sql-prepared-statements.html), [privilege system](https://dev.mysql.com/doc/refman/8.4/en/privilege-system.html), and [INSERT ... ON DUPLICATE KEY UPDATE](https://dev.mysql.com/doc/refman/8.4/en/insert-on-duplicate.html).
