# Mixed Interview Scenarios And Mock Round

[Exercises](24-mixed-interview-scenarios-exercises.md) | [Topic index](../start.md)

## Interview Answer

For a mixed MySQL question, I first restate the result grain and correctness rules, then write a clear query or transaction outline. I explain why the chosen join, aggregate, key, or index fits, identify NULLs/ties/concurrency risks, and mention how I would verify performance. A strong answer is not just syntax: it states assumptions and a practical failure or edge case.

## A Repeatable Approach

1. Clarify entities, output columns, one-to-many relationships, optional matches, ordering, and boundary rules.
2. Sketch the correct result using explicit joins, grouping, or a subquery/window function. Decide whether to retain unmatched rows and whether duplicates are meaningful.
3. Protect invariants with keys/constraints and use one short transaction for writes that must succeed together. Prefer atomic conditional updates for inventory/balances.
4. Add an index only for a real filter/join/order pattern; inspect EXPLAIN with representative data and parameters.
5. State the limitation: nullable values, tied timestamps, empty groups, duplicate children, replica lag, transaction retries, or data growth.

## Minimal Example

A customer report needs every customer and paid-order count, including zero:

```sql
SELECT c.customer_id, COUNT(o.order_id) AS paid_orders
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
 AND o.status = 'paid'
GROUP BY c.customer_id
ORDER BY c.customer_id;
```

The status condition is in ON to keep customers without paid orders; COUNT of the non-NULL order key reports zero for an unmatched row.

## Common Traps

- Do not aggregate parent measures after joining multiple one-to-many children without controlling multiplication.
- Do not use COUNT(*) for unmatched rows in an outer-join count.
- Do not select an arbitrary latest row from MAX(date) without handling ties and choosing a deterministic key.
- Do not claim an index or isolation level guarantees an outcome without matching the actual predicate, engine, and transaction schedule.
- Do not treat file creation or browser checkboxes as evidence that the topic is mastered; explain and solve without notes.

## Mock-Round Expectations

Keep explanations concise: definition/mechanism, selected approach, and trade-off. When uncertain, state a reasonable assumption and show how the query changes if the requirement differs. For performance answers, use evidence (plan, row counts, latency) rather than “indexes make it faster.” For concurrency, identify sessions and statement order.

## Likely Follow-Ups

**What if the requirement changes from one row per customer to one row per order?** Change the output grain and grouping; make sure joins don't multiply order measures.

**What would you say when a query is correct but slow?** Measure with realistic inputs, inspect EXPLAIN, identify excess work, change one thing, and compare.

**How do you make a write safe to retry?** Use a transaction plus an idempotency key/unique constraint and check the authoritative operation state.

## References

Examples synthesize MySQL 8.4 behaviors documented in the [MySQL reference manual](https://dev.mysql.com/doc/refman/8.4/en/). Related revision topics include [joins](06-joins-missing-data.md), [aggregation](05-aggregation-reporting.md), [transactions](15-transactions-acid.md), and [index design](13-index-design.md).
