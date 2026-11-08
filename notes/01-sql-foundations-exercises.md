# SQL Foundations And Execution Order: Exercises

[Notes](01-sql-foundations.md) | [Topic index](../start.md)

12 questions: 7 query tasks, 3 debugging/edge cases, and 2 interview questions. Use a fresh MySQL 8.4 practice schema; all result order is stated explicitly.

## Setup

```sql
CREATE TABLE foundation_orders (
 order_id INT PRIMARY KEY, customer_id INT NOT NULL,
 status VARCHAR(16) NOT NULL, amount DECIMAL(8,2) NOT NULL
);
INSERT INTO foundation_orders VALUES
 (1,10,'paid',100),(2,10,'paid',50),(3,10,'pending',25),(4,20,'paid',75);
```

## 1. Select Paid Orders

Return order ID and amount for paid orders, ascending by ID.

**Expected result:** IDs 1, 2, and 4.

<details><summary>Show answer</summary>

```sql
SELECT order_id,amount FROM foundation_orders WHERE status='paid' ORDER BY order_id;
```
WHERE filters input rows.
</details>

## 2. Count Orders Per Customer

Return customer ID and order count, ordered by customer ID.

**Expected result:** Customer 10 has 3; customer 20 has 1.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,COUNT(*) AS order_count FROM foundation_orders
GROUP BY customer_id ORDER BY customer_id;
```
GROUP BY produces one row per customer group.
</details>

## 3. Filter Groups By Count

Return customers with at least two orders.

**Expected result:** Customer 10 only.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,COUNT(*) AS order_count FROM foundation_orders
GROUP BY customer_id HAVING COUNT(*)>=2 ORDER BY customer_id;
```
HAVING filters aggregate groups.
</details>

## 4. Sort And Limit Paid Orders

Return the two highest-amount paid orders, breaking ties by order ID.

**Expected result:** Order 1, then order 2.

<details><summary>Show answer</summary>

```sql
SELECT order_id,amount FROM foundation_orders WHERE status='paid'
ORDER BY amount DESC,order_id LIMIT 2;
```
The unique ID makes tied ordering deterministic.
</details>

## 5. Count Paid Orders Per Customer

Return customer IDs that have at least one paid order and their paid count.

**Expected result:** Customer 10 count 2; customer 20 count 1.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,COUNT(*) AS paid_count FROM foundation_orders
WHERE status='paid' GROUP BY customer_id ORDER BY customer_id;
```
The status predicate runs before grouping.
</details>

## 6. Find Customers With Paid Total Above 100

Return customer ID and paid total only when the total exceeds 100.

**Expected result:** Customer 10 with 150.00.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,SUM(amount) AS paid_total FROM foundation_orders
WHERE status='paid' GROUP BY customer_id HAVING SUM(amount)>100 ORDER BY customer_id;
```
The aggregate threshold belongs in HAVING.
</details>

## 7. Select Distinct Statuses

Return each stored status once, alphabetically.

**Expected result:** paid, pending.

<details><summary>Show answer</summary>

```sql
SELECT DISTINCT status FROM foundation_orders ORDER BY status;
```
DISTINCT applies to the selected status values.
</details>

## 8. Debug An Alias In WHERE

Why is `SELECT amount*2 AS doubled FROM foundation_orders WHERE doubled>100` invalid? Correct it.

**Expected result:** Return rows whose amount is above 50.

<details><summary>Show answer</summary>

```sql
SELECT amount*2 AS doubled FROM foundation_orders WHERE amount*2>100;
```
WHERE is logically evaluated before the SELECT alias exists.
</details>

## 9. Debug Aggregate Filtering

Correct `SELECT customer_id,COUNT(*) AS n FROM foundation_orders WHERE n>=2 GROUP BY customer_id`.

**Expected result:** Customer 10 and count 3.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,COUNT(*) AS n FROM foundation_orders
GROUP BY customer_id HAVING COUNT(*)>=2 ORDER BY customer_id;
```
Use HAVING for group aggregates.
</details>

## 10. Identify Unspecified Ordering

Does `SELECT order_id FROM foundation_orders LIMIT 2` guarantee orders 1 and 2?

**Expected result:** No; add ORDER BY with a tie-breaker.

<details><summary>Show answer</summary>

```sql
SELECT order_id FROM foundation_orders ORDER BY order_id LIMIT 2;
```
Without ORDER BY, row order is unspecified.
</details>

## 11. Interview: SQL Versus MySQL

Distinguish SQL from MySQL in one practical answer.

**Expected result:** Describe SQL as a language and MySQL as a database system/dialect implementation.

<details><summary>Show answer</summary>

SQL is a language for working with relational databases. MySQL is a database server that implements SQL and provides engine, transaction, type, and dialect-specific behavior; syntax and features may differ among database products.
</details>

## 12. Interview: Logical Versus Physical Order

Why learn SELECT's logical clause order if the optimizer can reorder work?

**Expected result:** Explain semantic reasoning versus physical execution.

<details><summary>Show answer</summary>

Logical order explains name/aggregate visibility and query meaning, such as why WHERE cannot use a SELECT alias. The optimizer may choose a different physical plan as long as it preserves the query's result semantics.
</details>
