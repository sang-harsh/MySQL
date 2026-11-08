# Isolation Levels And MVCC

[Exercises](16-isolation-mvcc-exercises.md) | [Topic index](../start.md)

## Interview Answer

Isolation controls how concurrent transactions observe each other's work. InnoDB uses MVCC for consistent reads and defaults to REPEATABLE READ in MySQL 8.4; a transaction's consistent reads generally see a snapshot, while locking reads and writes acquire locks. I explain anomalies using a specific schedule and distinguish snapshot reads from `SELECT ... FOR UPDATE` when the application must safely change a row.

## Key Points

- READ UNCOMMITTED may expose uncommitted changes (dirty reads); READ COMMITTED gives each consistent read a fresh snapshot; REPEATABLE READ uses a consistent snapshot for ordinary reads in a transaction; SERIALIZABLE is stricter and can add blocking.
- InnoDB's default is REPEATABLE READ. At transaction start or first consistent read, a snapshot governs subsequent consistent reads; precise timing depends on transaction/access pattern.
- MVCC lets ordinary consistent reads see a snapshot without blocking writers in many cases. It does not mean writes never block or that all reads see the newest committed row.
- A locking read such as `SELECT ... FOR UPDATE` reads current rows and locks them for a transaction, useful before a dependent update. It must run in a transaction and use an appropriate index/predicate.
- A non-repeatable read means rereading a row gives a changed committed value; a phantom involves a changed set of rows matching a predicate. InnoDB's gap/next-key locking behavior can matter for locking reads under REPEATABLE READ.
- Lost updates can occur when applications read, compute, then overwrite without coordination. Use atomic conditional updates, version columns, or locking as appropriate.
- Isolation level alone does not replace constraints and business-rule checks.

## Two-Session Sketch

At READ COMMITTED, Session A begins and reads stock=5. Session B updates stock to 4 and commits. A's next consistent read may see 4 because each read gets a new snapshot at this isolation level. At REPEATABLE READ, A's ordinary consistent read generally continues to see its earlier snapshot; a locking read is a different access path.

## Common Traps

- Do not say REPEATABLE READ means every statement sees the latest committed data; consistent snapshot reads and current locking reads differ.
- A transaction started in one application method but executed on multiple connections does not share an isolation context.
- READ COMMITTED reduces some locking but does not automatically prevent lost updates or all races.
- Exact anomaly terminology is standard, but implementation behavior varies by engine; identify InnoDB and the read type.

## Likely Follow-Ups

**What is MVCC?** Multi-Version Concurrency Control keeps row versions so consistent reads can observe a snapshot while other transactions modify rows.

**What differs between READ COMMITTED and REPEATABLE READ?** In READ COMMITTED, each consistent read gets a new snapshot; REPEATABLE READ generally keeps a transaction snapshot for consistent reads.

**When use FOR UPDATE?** When a transaction must read current rows and lock them before making a dependent decision/update, such as reserving stock.

## MySQL References

Examples target MySQL 8.4/InnoDB. See [InnoDB transaction isolation levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html) and [consistent reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html).
