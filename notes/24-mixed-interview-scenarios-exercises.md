# Mixed Interview Scenarios And Mock Round: Exercises

[Notes](24-mixed-interview-scenarios.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 query/diagnostic/transaction tasks, and 2 interview questions. Target MySQL 8.4/InnoDB. Use the fixture in an isolated practice schema; all dates are fixed and output ordering is explicit.

## Setup

```sql
CREATE TABLE mock_customers (customer_id INT PRIMARY KEY, name VARCHAR(40) NOT NULL);
CREATE TABLE mock_orders (
 order_id INT PRIMARY KEY, customer_id INT NULL, status VARCHAR(16) NOT NULL,
 amount DECIMAL(8,2) NOT NULL, ordered_at DATETIME NOT NULL
);
CREATE TABLE mock_payments (
 payment_id INT PRIMARY KEY, order_id INT NOT NULL, amount DECIMAL(8,2) NOT NULL
);
CREATE TABLE mock_inventory (product_id INT PRIMARY KEY, available INT NOT NULL);
INSERT INTO mock_customers VALUES (1,'Asha'),(2,'Bharat'),(3,'Charu');
INSERT INTO mock_orders VALUES
 (101,1,'paid',100,'2026-10-01 10:00:00'),(102,1,'pending',50,'2026-10-02 10:00:00'),
 (103,2,'paid',75,'2026-10-03 10:00:00'),(104,NULL,'paid',20,'2026-10-04 10:00:00');
INSERT INTO mock_payments VALUES (501,101,60),(502,101,40),(503,103,75);
INSERT INTO mock_inventory VALUES (9,1);
```

## 1. Paid Order Count Per Customer

Show every customer and paid-order count, including customers with none.

**Expected result:** Asha 1, Bharat 1, Charu 0.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,COUNT(o.order_id) AS paid_count
FROM mock_customers c LEFT JOIN mock_orders o
 ON o.customer_id=c.customer_id AND o.status='paid'
GROUP BY c.customer_id ORDER BY c.customer_id;
```
Filter paid matches in ON and count a non-NULL order key.
</details>

## 2. Find Customers Without Orders

Return IDs and names of registered customers with no orders.

**Expected result:** Charu only.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,c.name FROM mock_customers c
WHERE NOT EXISTS (SELECT 1 FROM mock_orders o WHERE o.customer_id=c.customer_id)
ORDER BY c.customer_id;
```
NOT EXISTS expresses the anti-match; the guest order has no registered customer.
</details>

## 3. Latest Order Per Customer, Ties Included

Return all customer orders at that customer's latest timestamp.

**Expected result:** Asha's order 102 and Bharat's order 103.

<details><summary>Show answer</summary>

```sql
SELECT o.order_id,o.customer_id,o.ordered_at FROM mock_orders o
WHERE o.customer_id IS NOT NULL AND o.ordered_at=(
 SELECT MAX(o2.ordered_at) FROM mock_orders o2 WHERE o2.customer_id=o.customer_id
) ORDER BY o.customer_id,o.order_id;
```
This keeps ties at the maximum time; add ROW_NUMBER with an ID tie-breaker if exactly one is required.
</details>

## 4. Customer Paid-Order Total

Return each customer and their paid order amount total, including zero for no paid orders.

**Expected result:** 100.00, 75.00, and 0.00 for customers 1, 2, and 3.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,COALESCE(SUM(o.amount),0.00) AS paid_total
FROM mock_customers c LEFT JOIN mock_orders o
 ON o.customer_id=c.customer_id AND o.status='paid'
GROUP BY c.customer_id ORDER BY c.customer_id;
```
The join preserves customers; COALESCE displays zero for no matching paid rows.
</details>

## 5. Preserve Order Totals When Joining Payments

Return each registered order ID and its payment total without inflating the order amount.

**Expected result:** Order 101 has payment total 100.00, order 102 has 0.00, order 103 has 75.00.

<details><summary>Show answer</summary>

```sql
SELECT o.order_id,COALESCE(SUM(p.amount),0.00) AS paid_amount
FROM mock_orders o LEFT JOIN mock_payments p ON p.order_id=o.order_id
WHERE o.customer_id IS NOT NULL
GROUP BY o.order_id ORDER BY o.order_id;
```
Aggregate payment amounts only; don't sum order.amount across repeated payment rows.
</details>

## 6. Find Orders Above Average

Return registered order IDs whose order amount is above the average of all orders, including guest orders.

**Expected result:** Orders 101 and 103.

<details><summary>Show answer</summary>

```sql
SELECT order_id,amount FROM mock_orders
WHERE customer_id IS NOT NULL AND amount>(SELECT AVG(amount) FROM mock_orders)
ORDER BY order_id;
```
The average includes guest order 104 as specified.
</details>

## 7. Reserve The Last Inventory Unit

Write an atomic update to reserve one unit of product 9 and state how success is determined.

**Expected result:** One update succeeds; check affected rows for exactly one.

<details><summary>Show answer</summary>

```sql
UPDATE mock_inventory SET available=available-1
WHERE product_id=9 AND available>=1;
```
Check affected rows; a second concurrent request cannot decrement below zero.
</details>

## 8. Propose An Index For Customer Order History

The endpoint filters by customer ID, sorts newest first, and returns order ID/time. Propose a candidate index and evidence to check.

**Expected result:** Candidate `(customer_id, ordered_at)`; inspect EXPLAIN and representative workload.

<details><summary>Show answer</summary>

```sql
CREATE INDEX ix_mock_orders_customer_date ON mock_orders(customer_id,ordered_at);
```
Use EXPLAIN and realistic data to confirm selectivity/sorting benefit. Weigh write and storage costs; don't assume the optimizer must use it.
</details>

## 9. Debug The Customer Count

Why does COUNT(*) report one for a customer with no paid order in an outer join? Correct it.

**Expected result:** Count the nullable right-side order primary key; Charu becomes zero.

<details><summary>Show answer</summary>

```sql
COUNT(o.order_id)
```
A LEFT JOIN creates one NULL-extended row for Charu, counted by COUNT(*), while COUNT(order_id) ignores the NULL key.
</details>

## 10. Explain A Read-After-Write Risk

A just-created order is read from an asynchronous replica and is missing. Give a likely explanation and safe response.

**Expected result:** Replica lag; read from primary or use a consistency mechanism.

<details><summary>Show answer</summary>

The replica may not have applied the commit yet. Read from the primary or wait for a validated replication position; do not assume the write failed and repeat non-idempotent work.
</details>

## 11. Interview: Structure A Query Answer

State a quick method for answering an unfamiliar multi-table SQL question.

**Expected result:** Clarify grain/NULL/ties/order, express query, then explain edge case/performance evidence.

<details><summary>Show answer</summary>

Clarify the output grain, relationship cardinality, missing matches, tie/order rules, and NULL meaning. Write an explicit query, explain why filters belong where they do, then name one edge case and how you would verify performance if relevant.
</details>

## 12. Interview: Safe Transaction Retry

A deadlock rolls back an order/inventory transaction. What does a safe retry require?

**Expected result:** Retry the full transaction, bounded, with idempotent request handling and affected-row checks.

<details><summary>Show answer</summary>

Retry the entire transaction with bounded backoff only when the operation is safe to repeat. Use a request idempotency key/unique constraint, check conditional update row counts, and keep remote side effects outside the retried transaction or make them idempotent.
</details>
