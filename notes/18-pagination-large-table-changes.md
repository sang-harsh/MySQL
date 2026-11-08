# Pagination And Large-Table Changes

[Exercises](18-pagination-large-table-changes-exercises.md) | [Topic index](../start.md)

## Interview Answer

Offset pagination is easy to understand and works well for small result sets, but deep offsets require the server to find and skip many rows. Keyset pagination resumes after the last seen ordering key, making it better for growing feeds when ordering is stable. For large changes, process bounded batches with deterministic keys, observe load, and make the operation resumable instead of issuing one unbounded update or delete.

## Key Points

- `LIMIT size OFFSET offset` is simple for page-number navigation. Always use deterministic ordering with a unique tie-breaker; inserts/deletes between requests can shift page contents.
- Keyset pagination uses the last row's key, such as `(created_at, order_id)`, and seeks to the next range. The ordering columns should be stable and indexed.
- For descending order, continue with a lexicographic condition matching the sort: timestamp less than last timestamp, or equal timestamp and ID less than last ID.
- Keyset pagination doesn't naturally jump to an arbitrary page number. It is well-suited to next/previous feeds rather than page-number UX.
- Large UPDATE/DELETE operations can hold locks, generate undo/redo, and create replication lag. Batch by primary key or bounded time ranges and commit periodically.
- A resumable job records progress and handles retries idempotently. Recheck affected-row counts and business constraints.
- Online DDL support depends on operation, engine, and version; “online” does not mean no resource cost or no metadata lock.

## Minimal Examples

Offset page:

```sql
SELECT order_id, created_at FROM orders
ORDER BY created_at DESC, order_id DESC LIMIT 50 OFFSET 10000;
```

Keyset continuation after a row:

```sql
SELECT order_id, created_at FROM orders
WHERE created_at < ?
   OR (created_at = ? AND order_id < ?)
ORDER BY created_at DESC, order_id DESC LIMIT 50;
```

Bind the cursor values through an application prepared statement; an index on `(created_at, order_id)` can support this ordering. The `?` markers are prepared-statement syntax, not values to paste into a MySQL prompt.

## Common Traps

- LIMIT without a unique ordering can duplicate or skip rows even on a static dataset.
- Offset pages can shift while records are inserted or removed between requests.
- Keyset pagination cannot jump directly to page 500 without separately locating its cursor.
- A batch job must avoid repeatedly selecting the same rows; track last processed key or mark work atomically.

## Likely Follow-Ups

**When keep OFFSET?** Small lists, page-number navigation, or modest data where simplicity is more valuable than deep-page cost.

**How batch a delete?** Select a bounded ordered set of IDs, delete only those IDs in a transaction, commit, and continue from a recorded cursor while monitoring impact.

**Does online DDL eliminate blocking?** No. It may permit concurrent DML for supported operations but still consumes resources and can wait for metadata locks.

## MySQL Reference

Examples target MySQL 8.4. See [LIMIT optimization](https://dev.mysql.com/doc/refman/8.4/en/limit-optimization.html) and [online DDL](https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html).
