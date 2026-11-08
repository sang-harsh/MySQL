# Locks, Deadlocks, And Safe Writes

[Exercises](17-locks-deadlocks-safe-writes-exercises.md) | [Topic index](../start.md)

## Interview Answer

InnoDB locks rows (and sometimes index ranges) to coordinate concurrent writes. A safe inventory update is often a single conditional statement that changes stock only when enough remains, then checks affected rows. When a transaction must read before deciding, use a locking read in a short transaction. Deadlocks are expected concurrency outcomes: make transactions consistent and small, then retry the entire idempotent transaction with a bounded policy.

## Key Points

- `SELECT ... FOR UPDATE` is a locking read that holds locks until commit/rollback; use it inside a transaction when a later decision depends on the current row.
- An atomic conditional UPDATE can combine validation and mutation: `... WHERE stock >= quantity`. Check whether exactly one row changed.
- Optimistic concurrency uses a version column: update with `WHERE id=? AND version=?`, increment version, and treat zero affected rows as a conflict.
- InnoDB can lock index records and, depending on isolation, ranges/gaps. Indexes and predicates affect the lock footprint; do not promise every query locks exactly one row without inspecting the plan.
- A deadlock occurs when transactions form a wait cycle. InnoDB detects it and rolls back a victim transaction; the application should retry the full transaction when safe.
- Reduce deadlocks by keeping transactions short, accessing rows in a consistent order, and using selective indexed predicates. This reduces risk but cannot eliminate every deadlock.
- NOWAIT and SKIP LOCKED are available in MySQL 8.0+ for locking reads; SKIP LOCKED is useful for work queues but intentionally omits locked rows.
- Gap/next-key locks and metadata locks are useful recognition topics; reason at the statement/plan level rather than memorizing simplistic lock guarantees.

## Minimal Example

```sql
UPDATE inventory
SET available = available - 2
WHERE product_id = 42 AND available >= 2;
```

If one row changed, the reservation succeeded; if zero rows changed, the item is missing or stock is insufficient. Run related order writes in a transaction and add idempotency protection for request retries.

## Two-Session Sketch

Session A locks row 1 then requests row 2. Session B locks row 2 then requests row 1. Each waits for the other; InnoDB detects the cycle and rolls back one transaction. If both sessions lock rows in the same order, this particular cycle is avoided.

## Common Traps

- A prior ordinary SELECT does not reserve a row for a later update; use an atomic UPDATE or locking read.
- Retrying only the last statement after a deadlock may leave the business operation inconsistent; retry the full transaction.
- SKIP LOCKED can make a queue worker skip busy jobs temporarily; it does not mean those rows do not exist.
- Application-level retries need backoff, limits, and idempotent side effects.

## Likely Follow-Ups

**What is optimistic locking?** Compare a stored version on update and increment it only when the expected version matches; a zero-row result signals a concurrent change.

**How reduce deadlocks?** Keep transactions short, acquire rows in consistent order, and use selective indexes; still handle deadlock victims safely.

**When use SKIP LOCKED?** For independent queue jobs where workers can claim other available rows rather than wait; not for queries requiring a complete consistent result.

## MySQL Reference

Examples target MySQL 8.4/InnoDB. See [locking reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html), [deadlocks](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html), and [InnoDB locks](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html).
