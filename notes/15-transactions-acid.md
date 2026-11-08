# Transactions And ACID

[Exercises](15-transactions-acid-exercises.md) | [Topic index](../start.md)

## Interview Answer

A transaction groups related database operations into one unit: either the whole unit commits or its uncommitted changes are rolled back. ACID describes atomicity, consistency, isolation, and durability. In an order/payment workflow, I keep the writes that must succeed together in one short InnoDB transaction, validate business rules, and commit only after every required step succeeds.

## Key Points

- `START TRANSACTION` begins an explicit transaction; `COMMIT` makes it durable; `ROLLBACK` abandons its uncommitted changes. Autocommit is enabled by default for ordinary statements unless a transaction is explicitly started or configuration differs.
- Savepoints allow partial rollback within a transaction using `SAVEPOINT`, `ROLLBACK TO SAVEPOINT`, and `RELEASE SAVEPOINT`; they do not commit work.
- Atomicity: all-or-nothing. Consistency: constraints and application rules remain satisfied. Isolation: concurrent transactions do not observe prohibited intermediate states. Durability: committed work survives supported failures.
- Keep transactions short. External API calls, user input, and long computations while holding locks increase contention.
- Use the same database connection/session for all transaction statements. Returning a connection to a pool mid-transaction can break correctness.
- In MySQL, many DDL statements cause implicit commits. Atomic DDL in MySQL 8.0 protects supported DDL operations against partial crash effects, but does not make them rollback-able with a user's transaction.
- A transaction does not automatically prevent every logical race; use appropriate constraints, locking reads, or atomic conditional updates.

## Minimal Example

```sql
START TRANSACTION;
UPDATE inventory SET available = available - 1
WHERE product_id = 42 AND available > 0;
-- Application checks that exactly one row changed.
INSERT INTO order_items(order_id, product_id, quantity)
VALUES (9001, 42, 1);
COMMIT;
```

If the conditional update changes zero rows, the application should roll back rather than create an order without inventory. Production code must handle errors and deadlocks on the same connection.

## Common Traps

- Catching an error and continuing to COMMIT can persist only part of the intended workflow.
- ROLLBACK cannot undo an already committed transaction or generally reverse DDL that implicitly committed.
- A transaction boundary is per connection, not per application method name.
- Retrying a failed transaction is safe only when the operation is designed for retry, often with idempotency protection.

## Likely Follow-Ups

**What is a savepoint?** A named point inside an open transaction to which the session can roll back part of its work; the outer transaction remains open.

**Does autocommit prevent transactions?** No. An explicit transaction groups statements until COMMIT or ROLLBACK; autocommit applies to statements outside that transaction.

**What if COMMIT returns a network error?** The client may not know whether the server committed. Use an idempotency key or query authoritative state before retrying blindly.

## MySQL Reference

Examples target MySQL 8.4 with InnoDB. See [START TRANSACTION, COMMIT, and ROLLBACK](https://dev.mysql.com/doc/refman/8.4/en/commit.html) and [implicit commits](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html).
