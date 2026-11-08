# InnoDB Architecture And Storage: Exercises

[Notes](12-innodb-architecture.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 conceptual/diagnostic tasks, and 2 interview questions. Keep answers at application-developer depth; no server tuning or destructive operations are required.

## 1. Choose An Engine For Orders

A new order table needs transactions, foreign keys, and row-level concurrency. Which MySQL engine is appropriate?

**Expected result:** InnoDB.

<details><summary>Show answer</summary>

```sql
CREATE TABLE orders (order_id BIGINT PRIMARY KEY) ENGINE=InnoDB;
```
InnoDB supports transactions, foreign keys, crash recovery, and row-level locking behavior.
</details>

## 2. Understand A Wide Primary Key

A table uses a 300-byte natural string primary key and has many secondary indexes. What is the likely storage trade-off?

**Expected result:** Secondary indexes become larger because they carry the primary-key value.

<details><summary>Show answer</summary>

InnoDB secondary index entries include the primary-key columns, so a wide key increases every secondary index's footprint and can increase I/O. Consider a shorter surrogate key while retaining a UNIQUE constraint for the natural key.
</details>

## 3. Explain Buffer Pool Benefit

A frequently used index fits in memory after warm-up. What component helps avoid repeated physical reads?

**Expected result:** InnoDB buffer pool caches data/index pages.

<details><summary>Show answer</summary>

The InnoDB buffer pool caches pages containing table and index data. It reduces disk reads for repeated access but does not replace durable storage, logging, or backups.
</details>

## 4. Recover After A Crash

At a high level, what is redo logging for?

**Expected result:** Crash recovery can reapply committed changes as needed; don't confuse redo with backups or binlog.

<details><summary>Show answer</summary>

Redo records support InnoDB crash recovery by replaying logged changes needed to restore a consistent database state. They are distinct from undo information and the binary log, and they are not a backup strategy.
</details>

## 5. Support A Consistent Read

What role does undo information play at a high level?

**Expected result:** Older row versions support rollback and MVCC consistent reads.

<details><summary>Show answer</summary>

Undo information supports rolling back changes and reconstructing earlier row versions for consistent reads. Exact internals are optional for application interviews.
</details>

## 6. Select A Customer's Orders

A query filters orders by customer_id. Which index is a reasonable starting point, and what must still be checked?

**Expected result:** A secondary index on customer_id; verify workload/plan and storage-write costs.

<details><summary>Show answer</summary>

```sql
CREATE INDEX ix_orders_customer ON orders(customer_id);
```
Check real query selectivity and EXPLAIN. The index adds storage and write maintenance; it is not automatically beneficial for every workload.
</details>

## 7. Explain Clustered Storage

In InnoDB, what does it mean that the primary key is clustered?

**Expected result:** Table rows are organized in the primary-key index structure.

<details><summary>Show answer</summary>

The clustered primary-key index contains the row data in key order. If no suitable key is defined, InnoDB creates an internal row identifier; an explicit stable primary key is clearer for applications.
</details>

## 8. Distinguish Log Roles

At recognition level, compare undo, redo, and binary log purposes.

**Expected result:** Undo for rollback/versions, redo for crash recovery, binlog for replication/PITR workflows.

<details><summary>Show answer</summary>

Undo supports rollback and older row versions; redo supports InnoDB crash recovery; the binary log records server changes for replication and point-in-time recovery workflows. They are not interchangeable.
</details>

## 9. Debug “Row-Level Means One Row”

Is every InnoDB write guaranteed to lock only one row?

**Expected result:** No; index ranges and predicate access affect locks.

<details><summary>Show answer</summary>

No. Locks can involve index records and ranges depending on the operation, isolation, and access path. Use selective indexed predicates and reason from the statement and execution plan.
</details>

## 10. Debug “Buffer Pool Is A Backup”

Does a warm buffer pool protect against data loss like a backup?

**Expected result:** No; it is memory cache, not a backup or durable recovery copy.

<details><summary>Show answer</summary>

No. The buffer pool caches pages for performance. Backups and tested restore procedures are needed for recovery from data loss or corruption.
</details>

## 11. Interview: InnoDB Versus MyISAM

Give a short application-focused comparison.

**Expected result:** Mention transactions, foreign keys, crash recovery, and typical new-table choice.

<details><summary>Show answer</summary>

InnoDB supports transactions, foreign keys, and crash recovery, so it is the standard choice for transactional application data. MyISAM is nontransactional and lacks InnoDB foreign-key behavior; use it only for a specific justified legacy/workload case.
</details>

## 12. Interview: Primary-Key Width

Why can a wide primary key hurt a table with many secondary indexes?

**Expected result:** Secondary indexes carry primary-key values, increasing footprint and access cost.

<details><summary>Show answer</summary>

InnoDB stores the primary-key value in secondary index entries so it can locate the clustered row. A wide key therefore expands secondary indexes, increasing storage and potentially I/O.
</details>
