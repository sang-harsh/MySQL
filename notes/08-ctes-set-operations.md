# CTEs And Set Operations

[Exercises](08-ctes-set-operations-exercises.md) | [Topic index](../start.md)

## Interview Answer

A common table expression names a query result for use by a statement, making multi-step logic easier to read and reuse within that statement. `UNION ALL` appends rows and preserves duplicates; `UNION` removes duplicate result rows. I check that each branch returns the same number of compatible columns in the same logical order, and I add a final ORDER BY when output ordering matters.

## Key Points

- A nonrecursive CTE uses `WITH name AS (query)` before a SELECT, INSERT, UPDATE, or DELETE. CTEs improve structure but do not inherently guarantee materialization or better performance.
- Multiple CTEs can build on earlier CTEs in the same WITH clause. Use clear names and avoid hiding a simple query behind unnecessary layers.
- A recursive CTE uses `WITH RECURSIVE` with an anchor query and recursive member, commonly for trees or sequences. Define a terminating condition and be mindful of recursion limits and row growth.
- `UNION ALL` combines rows without duplicate elimination and is usually cheaper when duplicates are meaningful or impossible by design.
- `UNION` performs duplicate elimination across the projected columns. It can remove legitimate repeated events if used without intent.
- Branches need the same column count; corresponding types must be compatible. Column names in the combined result come from the first SELECT.
- In MySQL 8.0, INTERSECT and EXCEPT are available starting in 8.0.31. Earlier 8.0 versions need alternatives such as joins or NOT EXISTS. MySQL 5.7 has no CTE support.

## Minimal Example

```sql
WITH customer_totals AS (
  SELECT customer_id, SUM(amount) AS total_amount
  FROM orders
  WHERE status = 'paid'
  GROUP BY customer_id
)
SELECT customer_id, total_amount
FROM customer_totals
WHERE total_amount >= 100
ORDER BY total_amount DESC, customer_id;
```

The CTE creates a readable aggregate stage. The final query filters that stage; a derived table could express the same logic, and the optimizer determines execution details.

## Common Traps

- A CTE is scoped to one statement, not a persistent view or temporary table.
- `UNION` can hide duplicates that reveal a join or data issue; use it only when set semantics are intended.
- Ordering within an individual branch does not guarantee final combined order; put ORDER BY on the complete query.
- Recursive CTEs need an explicit stopping rule and can expand rapidly in cyclic or malformed relationships.

## Likely Follow-Ups

**CTE or derived table?** Both can express an intermediate result. A CTE can make multi-step or reused logic clearer; neither syntax alone guarantees a faster plan.

**UNION or UNION ALL?** Use UNION ALL to preserve rows and avoid de-duplication; use UNION when duplicate projected rows should be collapsed.

**Can I reference a CTE more than once?** Yes, within the statement, but inspect the plan for performance-sensitive queries because the optimizer's treatment depends on the query and server version.

## MySQL References

Examples target MySQL 8.4. CTEs require MySQL 8.0+; INTERSECT and EXCEPT require 8.0.31+. See [WITH (CTE) syntax](https://dev.mysql.com/doc/refman/8.4/en/with.html) and [UNION clause](https://dev.mysql.com/doc/refman/8.4/en/union.html).
