# CTEs And Set Operations: Exercises

[Notes](08-ctes-set-operations.md) | [Topic index](../start.md)

12 questions: 7 query tasks, 3 debugging/edge cases, and 2 interview questions. Target MySQL 8.4. CTE syntax requires MySQL 8.0+; INTERSECT/EXCEPT syntax requires 8.0.31+. Ordering assumptions are stated per task.

## Setup

```sql
CREATE TABLE cte_orders (order_id INT PRIMARY KEY, customer_id INT NOT NULL, status VARCHAR(16) NOT NULL, amount DECIMAL(8,2) NOT NULL);
CREATE TABLE cte_imported (source_id INT PRIMARY KEY, email VARCHAR(80) NOT NULL);
CREATE TABLE cte_active (user_id INT PRIMARY KEY, email VARCHAR(80) NOT NULL);
INSERT INTO cte_orders VALUES (1,10,'paid',100),(2,10,'paid',50),(3,20,'pending',40);
INSERT INTO cte_imported VALUES (1,'a@example.test'),(2,'b@example.test');
INSERT INTO cte_active VALUES (10,'a@example.test'),(20,'c@example.test');
```

## 1. Name A Paid-Order Aggregate

Use a CTE to return customers with paid total at least 100.

**Expected result:** Customer 10 with 150.00.

<details><summary>Show answer</summary>

```sql
WITH totals AS (
 SELECT customer_id,SUM(amount) AS paid_total FROM cte_orders
 WHERE status='paid' GROUP BY customer_id
)
SELECT customer_id,paid_total FROM totals WHERE paid_total>=100 ORDER BY customer_id;
```
The CTE names the aggregate stage.
</details>

## 2. Split A Multi-Step Filter

Use a CTE to find paid orders, then return order IDs greater than 1.

**Expected result:** No rows.

<details><summary>Show answer</summary>

```sql
WITH paid_orders AS (
 SELECT order_id,customer_id,amount FROM cte_orders WHERE status='paid'
)
SELECT order_id FROM paid_orders WHERE order_id>1 ORDER BY order_id;
```
A CTE exists only for this statement.
</details>

## 3. Combine Source Rows Preserving Duplicates

Append imported and active emails in source order using UNION ALL.

**Expected result:** Four rows: a, b, a, c in that source sequence; final ordering is by source label and email.

<details><summary>Show answer</summary>

```sql
SELECT email,source FROM (
 SELECT email,'active' AS source FROM cte_active
 UNION ALL
 SELECT email,'imported' AS source FROM cte_imported
) AS combined
ORDER BY source,email;
```
UNION ALL preserves the email present in both tables.
</details>

## 4. Return Unique Emails From Both Tables

Return one row per distinct email appearing in either table.

**Expected result:** a, b, c example.test addresses, sorted alphabetically.

<details><summary>Show answer</summary>

```sql
SELECT email FROM cte_active
UNION
SELECT email FROM cte_imported
ORDER BY email;
```
UNION removes duplicate projected email values.
</details>

## 5. Find Emails Not Yet Active

Use NOT EXISTS to find imported emails absent from active users.

**Expected result:** b@example.test.

<details><summary>Show answer</summary>

```sql
SELECT i.email FROM cte_imported i
WHERE NOT EXISTS (SELECT 1 FROM cte_active a WHERE a.email=i.email)
ORDER BY i.email;
```
This anti-match avoids NULL-sensitive NOT IN behavior.
</details>

## 6. Use A Recursive Sequence

Generate integers 1 through 5 with a recursive CTE.

**Expected result:** Five rows containing 1, 2, 3, 4, and 5 in order.

<details><summary>Show answer</summary>

```sql
WITH RECURSIVE numbers(n) AS (
 SELECT 1 UNION ALL SELECT n+1 FROM numbers WHERE n<5
)
SELECT n FROM numbers ORDER BY n;
```
The predicate stops recursion at 5.
</details>

## 7. Build A Recursive Hierarchy Sketch

A `categories(category_id,parent_id)` tree should list a selected root and descendants. State the CTE shape.

**Expected result:** The anchor returns the root; each recursive step joins children to already returned IDs and recursion terminates when no children remain.

<details><summary>Show answer</summary>

```sql
WITH RECURSIVE tree AS (
 SELECT category_id,parent_id FROM categories WHERE category_id=10
 UNION ALL
 SELECT c.category_id,c.parent_id FROM categories c JOIN tree t ON c.parent_id=t.category_id
)
SELECT category_id,parent_id FROM tree ORDER BY category_id;
```
Acyclic parentage is assumed; malformed cycles need protection and controlled recursion depth.
</details>

## 8. Debug Mismatched UNION Columns

Why does a UNION fail if one branch selects `email` and the other selects `user_id,email`? Correct the shape.

**Expected result:** Both branches return the same number of corresponding columns.

<details><summary>Show answer</summary>

```sql
SELECT email FROM cte_active
UNION ALL
SELECT email FROM cte_imported;
```
Each branch must return the same column count with compatible positional types.
</details>

## 9. Debug Unwanted De-Duplication

A log report uses UNION and loses two identical event rows from separate sources. What change preserves both?

**Expected result:** Use UNION ALL.

<details><summary>Show answer</summary>

```sql
SELECT event_type,event_time FROM source_a
UNION ALL
SELECT event_type,event_time FROM source_b;
```
UNION removes duplicates across projected values; UNION ALL preserves source events.
</details>

## 10. Identify Version Support

Can MySQL 5.7 run a WITH CTE? When did MySQL 8.0 add INTERSECT and EXCEPT?

**Expected result:** CTEs are unavailable in 5.7; INTERSECT/EXCEPT arrived in MySQL 8.0.31.

<details><summary>Show answer</summary>

MySQL 5.7 requires a derived-table or other rewrite instead of CTE syntax. INTERSECT and EXCEPT are supported from MySQL 8.0.31; use joins/EXISTS alternatives on earlier versions.
</details>

## 11. Interview: UNION Versus UNION ALL

Explain the difference and typical cost implication.

**Expected result:** Cover duplicate elimination and preserving legitimate repeated rows.

<details><summary>Show answer</summary>

UNION removes duplicate projected rows; UNION ALL appends all rows, including duplicates. UNION may require extra de-duplication work, so use ALL when duplicates should remain or are impossible.
</details>

## 12. Interview: CTE Performance

Does a CTE automatically improve query performance?

**Expected result:** No; it improves structure, while plan behavior depends on optimizer and query.

<details><summary>Show answer</summary>

No. A CTE names a statement-local result and can clarify logic, but the optimizer decides how to execute it. Compare EXPLAIN plans on representative data if performance is the concern.
</details>
