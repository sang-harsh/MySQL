# EXPLAIN And Query Optimization

[Exercises](14-explain-query-optimization-exercises.md) | [Topic index](../start.md)

## Interview Answer

I start query optimization by confirming the result is correct, measuring the slow query with representative parameters, and inspecting its execution plan. `EXPLAIN` shows the optimizer's estimated access strategy, chosen key, and row estimates; it does not prove actual latency. I look for avoidable scans, excessive rows, poor join order, and non-sargable filters, then change one thing and measure again.

## Key Points

- `EXPLAIN SELECT ...` reports a plan without running the SELECT. `EXPLAIN ANALYZE` (MySQL 8.0.18+) executes the statement and reports actual timing/row information; use it carefully because it runs the query.
- Common fields include `type` (access method), `possible_keys`, `key`, `rows`, and `filtered`. JSON output gives more detail. A table scan is not automatically wrong, especially for small tables or low-selectivity filters.
- An index can reduce rows examined for selective predicates and joins. Composite index order should match real predicates and ordering; verify the selected key.
- Avoid `SELECT *` when the endpoint needs only a few columns; this can reduce row transfer and make covering access possible.
- Keep predicates sargable: compare a bare indexed column to a value/range instead of wrapping it in a function or forcing a conversion.
- Statistics and data distribution affect choices. Refreshing statistics may help after major changes, but do not use optimizer hints before understanding the plan.
- Measure with realistic parameter values and data volume. A query returning one row in a tiny development fixture may behave differently at production scale.

## Minimal Example

```sql
EXPLAIN
SELECT order_id, ordered_at
FROM orders
WHERE customer_id = 42
  AND ordered_at >= '2026-01-01'
ORDER BY ordered_at DESC
LIMIT 20;
```

Check whether a relevant key is selected and whether estimated rows look reasonable. An index such as `(customer_id, ordered_at)` may fit; confirm with the plan and workload rather than prescribing it blindly.

## Common Traps

- `EXPLAIN ANALYZE` executes the statement; avoid it on destructive or expensive statements unless the environment and impact are understood.
- `type=ALL` can be reasonable for a tiny table; `type=range` is not automatically best if most rows qualify.
- An index may be ignored because of selectivity, stale estimates, a function on the column, or mismatched composite order.
- Query speed is not only the access path; network transfer, locks, row width, and application N+1 behavior also matter.

## Likely Follow-Ups

**What does rows mean?** It is an estimate of rows examined at that plan step, not necessarily the exact returned count. Compare estimates with actuals where possible.

**Should I add the missing index immediately?** First confirm the query pattern, predicate selectivity, existing indexes, and write/storage cost; test a candidate index and compare plans/latency.

**What is sargable?** A predicate form that can use an index search/range efficiently, such as a bare indexed date column compared with a boundary value.

## MySQL Reference

Examples target MySQL 8.4. `EXPLAIN ANALYZE` requires MySQL 8.0.18+. See [EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html) and [optimization overview](https://dev.mysql.com/doc/refman/8.4/en/optimization.html).
