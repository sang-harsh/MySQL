# Aggregation And Conditional Reporting

[Exercises](05-aggregation-reporting-exercises.md) | [Topic index](../start.md)

## Interview Answer

Aggregate functions summarize rows into a smaller result, usually one row per group. `WHERE` filters source rows before grouping; `HAVING` filters groups after aggregate values are calculated. I first define the output grain, then make sure joins have not multiplied the rows being counted or summed.

## Key Points

- `COUNT(*)` counts rows; `COUNT(expr)` ignores NULL values; `COUNT(DISTINCT expr)` counts distinct non-NULL values.
- `SUM`, `AVG`, `MIN`, and `MAX` operate on a group. `SUM` and `AVG` return NULL when there are no non-NULL inputs.
- Every selected nonaggregate expression must be grouped or functionally dependent on grouped columns with MySQL's `ONLY_FULL_GROUP_BY` rules. Do not disable strict grouping just to get an arbitrary value.
- A conditional total can use `SUM(CASE WHEN condition THEN amount ELSE 0 END)`. Put predicates that restrict input rows in `WHERE`; use `HAVING` for an aggregate threshold.
- When joining two one-to-many children, each child's rows can multiply the other's. Pre-aggregate at the needed grain before joining, or aggregate from one child at a time.

## Minimal Example

```sql
SELECT customer_id,
       COUNT(*) AS order_count,
       SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS paid_amount
FROM report_orders
GROUP BY customer_id
HAVING COUNT(*) >= 1
ORDER BY customer_id;
```

The grouped result has one row per customer represented in `report_orders`; customers with no orders do not appear unless a customer table is left joined. For outer joins, `COUNT(*)` includes the NULL-extended row while `COUNT(order_id)` does not.

## Common Traps

- `WHERE SUM(amount) > ...` is invalid because WHERE runs before grouping; use HAVING.
- An outer join followed by `COUNT(*)` can report one row for a customer with no child match. Count a non-NULL child key.
- `SUM(DISTINCT amount)` de-duplicates values, not duplicated business entities, so equal legitimate amounts are lost.
- When reporting categories with no activity, start from the category/customer table and LEFT JOIN facts; use `COALESCE` only when zero is the intended display value.

## Likely Follow-Ups

**Can I select a name while grouping by customer ID?** In MySQL 8.4 with `ONLY_FULL_GROUP_BY`, it is accepted when the key establishes functional dependence, such as a primary key. Otherwise group the name too or select it after aggregating IDs.

**How do I count paid orders and all orders together?** Use `COUNT(*)` for all input orders and `SUM(status = 'paid')` or an explicit CASE expression for paid orders. The boolean expression is MySQL-specific shorthand; CASE is clearer across SQL dialects.

**Does GROUP BY sort output?** Do not rely on implicit ordering. Add an explicit `ORDER BY` with tie-breakers when result order matters.

## MySQL Reference

Examples target MySQL 8.4 with InnoDB, strict SQL mode, and `ONLY_FULL_GROUP_BY`. See [aggregate functions](https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html) and [GROUP BY handling](https://dev.mysql.com/doc/refman/8.4/en/group-by-handling.html).
