# Subqueries And Existence Checks

[Exercises](07-subqueries-existence-exercises.md) | [Topic index](../start.md)

## Interview Answer

A subquery is a query nested inside another statement; it can return a scalar, a set of values, or a derived table. I use `EXISTS` when the requirement is whether a related row exists, and `NOT EXISTS` for its absence. I check NULL behavior carefully with `NOT IN`, and compare plans only when performance is a concern rather than assuming joins or subqueries are always faster.

## Key Points

- A scalar subquery must return at most one row; a multirow result causes an error. Aggregate functions such as `MAX` naturally return one row.
- An uncorrelated subquery can be evaluated independently. A correlated subquery references an outer row; the optimizer may transform it, so do not equate correlation automatically with a slow nested loop.
- A derived table is a subquery in `FROM` and must have an alias in MySQL. A CTE is another way to name a query result.
- `EXISTS` tests whether its subquery returns any row; selected values inside it do not matter.
- `NOT IN` can evaluate to UNKNOWN if the candidate set contains NULL. `NOT EXISTS` with an explicit equality condition is usually safer for anti-matching.
- An ordinary equality does not match NULL to NULL; express NULL business rules intentionally.

## Minimal Example

Find customers with at least one paid order:

```sql
SELECT c.customer_id, c.name
FROM sub_customers AS c
WHERE EXISTS (
  SELECT 1 FROM sub_orders AS o
  WHERE o.customer_id = c.customer_id AND o.status = 'paid'
)
ORDER BY c.customer_id;
```

`EXISTS` returns each customer once regardless of how many paid orders match. A join would return one row per matching order unless the query groups or de-duplicates at the customer grain.

## Common Traps

- If a scalar subquery has multiple rows, MySQL reports an error; add a correct aggregate or deterministic row selection.
- `NOT IN (SELECT nullable_column ...)` may return no true rows when a NULL is present. Use `NOT EXISTS`, or prove the subquery column is NOT NULL.
- A correlated subquery can express a per-row comparison clearly, but indexes and data distribution affect the actual plan.
- Do not use `DISTINCT` to conceal a one-to-many join when EXISTS expresses the intended condition directly.

## Likely Follow-Ups

**When would you use a derived table?** When an intermediate result needs to be filtered or joined, such as pre-aggregated sales per customer. Give it a meaningful alias and keep the result grain clear.

**Is EXISTS faster than JOIN?** Not universally. They express different row-shaping needs; MySQL may optimize either form. Check `EXPLAIN` with representative data if the plan matters.

**What happens for an empty NOT IN subquery?** No candidate values exist, so the predicate is true for every outer value, including NULL under MySQL's empty-set semantics. Still prefer explicit NOT EXISTS when NULLs may occur in nonempty sets.

## MySQL References

Examples target MySQL 8.4. See [subquery syntax](https://dev.mysql.com/doc/refman/8.4/en/subqueries.html) and [EXISTS/NOT EXISTS](https://dev.mysql.com/doc/refman/8.4/en/exists-and-not-exists-subqueries.html). The described constructs are supported in MySQL 5.7 and 8.0 as well.
