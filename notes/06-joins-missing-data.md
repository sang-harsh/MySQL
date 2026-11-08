# Joins And Missing-Data Queries

[Exercises](06-joins-missing-data-exercises.md) | [Topic index](../start.md)

## Interview Answer

A join combines rows from tables using a matching condition. An INNER JOIN returns matching pairs; a LEFT JOIN also keeps unmatched left-side rows and fills the right-side columns with NULL. I choose the join based on which records the business needs to retain, and check relationship cardinality because multiple matches can repeat rows and inflate totals.

## Quick Diagnostic

If I LEFT JOIN customers to orders, then put `orders.status = 'paid'` in WHERE, will customers without paid orders remain? Explain before reading the answer in exercise 8.

## Key Points

| Join | Interview-ready meaning |
|---|---|
| INNER | Return one row for each matching pair; exclude missing matches. |
| LEFT | Keep every left row, even when no right row matches. |
| RIGHT | Keep every right row; swap the tables to express it as LEFT JOIN. |
| CROSS | Return every combination; 4 customers and 2 products produce 8 rows. |
| Self join | Join a table to itself using different aliases, such as employees and managers. |

**ON versus WHERE:** ON decides which rows match. WHERE filters the joined result. To retain every customer but attach only paid orders, put the paid-status condition in ON; putting it in WHERE removes NULL-extended rows. Conditions on the preserved customer's own attributes can still go in WHERE.

**Missing matches:** Use LEFT JOIN followed by `WHERE orders.order_id IS NULL`. Test a non-nullable right-side key, not an optional field such as a delivery date. A real row can contain an optional NULL without being a missing match. NOT EXISTS is another clear choice when only existence matters.

**Repeated rows:** One customer with two orders correctly produces two joined rows. When you join orders to multiple payment rows, an order amount repeats once per payment. Decide the required result level first: one row per customer, order, or payment; aggregate child rows before joining when necessary. DISTINCT is not a general repair for a wrong join or inflated SUM.

## Minimal Example

Use the shared exercise setup. Return every customer with only their paid orders:

```sql
SELECT customers.customer_id, customers.name, orders.order_id
FROM join_customers AS customers
LEFT JOIN join_orders AS orders
  ON orders.customer_id = customers.customer_id
 AND orders.status = 'paid'
ORDER BY customers.customer_id, orders.order_id;
```

```text
customer_id | name   | order_id
1           | Asha   | 101
2           | Bharat | 103
3           | Charu  | NULL
4           | Dev    | NULL
```

## Common Traps

- `NULL = NULL` is not true under ordinary equality. Guest orders with a NULL customer ID do not match registered customers.
- Forgetting ON can accidentally create combinations instead of matching records. Prefer explicit joins and qualified column names.
- COUNT(*) counts the placeholder row from an outer join; COUNT(orders.order_id) counts actual orders.
- MySQL has no native FULL OUTER JOIN. Combine a LEFT JOIN with unmatched rows from the other side using UNION ALL; do not include matched rows twice.

## Likely Follow-Ups

**Is LEFT JOIN faster than INNER JOIN?** Neither is universally faster. They answer different questions; choose the correct result first, then inspect indexes and the execution plan if performance matters.

**Can a self join use LEFT JOIN?** Yes. A LEFT self join lists employees even when they have no manager, whereas an INNER self join drops those employees.

**Why not use UNION for the full-join workaround?** UNION removes identical projected rows. UNION ALL preserves valid duplicates; the unmatched-only second branch prevents adding matched pairs twice.

## MySQL References

Generic SQL join semantics apply here. MySQL-specific syntax and NULL-extended rows: [MySQL 8.4 JOIN clause](https://dev.mysql.com/doc/refman/8.4/en/join.html). Right-side WHERE predicates can simplify an outer join to an inner join: [outer join simplification](https://dev.mysql.com/doc/refman/8.4/en/outer-join-simplification.html). Examples target MySQL 8.4/InnoDB; these join patterns also work in MySQL 5.7 and 8.0.