# Index Design

[Exercises](13-index-design-exercises.md) | [Topic index](../start.md)

## Interview Answer

An index is an ordered data structure that helps MySQL find rows without scanning the whole table, but it costs storage and makes writes more expensive. In InnoDB, the primary key is clustered with the row data, while secondary-index entries also carry the primary-key value. I design indexes around actual filters, joins, and ordering, then verify the chosen plan with EXPLAIN.

## Key Points

- A primary key is the clustered index in InnoDB. Secondary indexes locate primary-key values, which are then used to reach the row.
- A composite index on `(a,b,c)` can efficiently support leftmost prefixes such as `a` and `(a,b)`, but generally not a lookup on `b` alone.
- Put equality predicates before range/order columns when the workload supports that order; index order is a workload decision, not a universal formula.
- A covering index contains all columns needed for a query, potentially avoiding row lookups, but adding columns increases size and write cost.
- Functions or type conversions applied to an indexed column can prevent a simple range lookup. Write sargable predicates when possible.
- Low-cardinality columns are not automatically useless; selectivity and the complete query matter. The optimizer may choose a table scan when it estimates that cheaper.
- MySQL can use an index for filtering, joins, and sometimes sorting/grouping. An index does not guarantee its use.

## Minimal Example

```sql
CREATE INDEX ix_orders_customer_status_date
  ON orders (customer_id, status, ordered_at);

SELECT order_id, ordered_at
FROM orders
WHERE customer_id = 42 AND status = 'paid'
ORDER BY ordered_at DESC;
```

This index begins with the equality columns and then the date used for ordering. Whether it fully satisfies the query depends on direction, selected columns, statistics, and the actual plan; validate it instead of assuming.

## Common Traps

- Indexing every column adds storage, slows writes, and complicates maintenance.
- An index on `(customer_id, ordered_at)` is not generally equivalent to one on `(ordered_at, customer_id)`.
- A leading wildcard such as `LIKE '%text'` cannot use a normal B-tree prefix lookup effectively.
- Redundant indexes should be evaluated carefully; a shorter index may still serve a distinct workload or constraint.

## Likely Follow-Ups

**Why keep a primary key short?** Its value is carried in secondary-index entries, so a wide key can enlarge every secondary index and increase I/O.

**What is a covering index?** An index that contains all columns needed by a query, including filtering and output, so MySQL may avoid fetching full rows.

**Why might MySQL ignore an index?** The table may be small, the predicate may match many rows, statistics may favor a scan, or the expression/order may not align with the index.

## MySQL Reference

Examples target MySQL 8.4/InnoDB. See [InnoDB indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-indexes.html), [multiple-column indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html), and [EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html).
