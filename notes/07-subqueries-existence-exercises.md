# Subqueries And Existence Checks: Exercises

[Notes](07-subqueries-existence.md) | [Topic index](../start.md)

12 questions: 7 scenario queries, 3 edge/debugging tasks, and 2 interview questions. Run in an isolated MySQL 8.4 schema. Questions are independent and ordered results are explicit.

## Setup

```sql
CREATE TABLE sub_customers (customer_id INT PRIMARY KEY, name VARCHAR(40) NOT NULL);
CREATE TABLE sub_orders (
 order_id INT PRIMARY KEY, customer_id INT NULL, status VARCHAR(16) NOT NULL,
 amount DECIMAL(8,2) NOT NULL
);
INSERT INTO sub_customers VALUES (1,'Asha'),(2,'Bharat'),(3,'Charu');
INSERT INTO sub_orders VALUES (101,1,'paid',100),(102,1,'pending',50),(103,2,'paid',75),(104,NULL,'paid',20);
```

## 1. Customers With Paid Orders

Return customers who have at least one paid order, once each.

**Expected result:** Asha and Bharat, ordered by ID.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,c.name FROM sub_customers c
WHERE EXISTS (SELECT 1 FROM sub_orders o WHERE o.customer_id=c.customer_id AND o.status='paid')
ORDER BY c.customer_id;
```
EXISTS tests matching rows without multiplying a customer with several matches.
</details>

## 2. Customers Without Orders

Return customers with no orders of any status.

**Expected result:** Charu only.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,c.name FROM sub_customers c
WHERE NOT EXISTS (SELECT 1 FROM sub_orders o WHERE o.customer_id=c.customer_id)
ORDER BY c.customer_id;
```
The guest order has NULL customer ID and is not related to a registered customer.
</details>

## 3. Orders Above The Overall Average

Return order IDs and amounts strictly above the average order amount.

**Expected result:** Orders 101 and 103.

<details><summary>Show answer</summary>

```sql
SELECT order_id,amount FROM sub_orders
WHERE amount > (SELECT AVG(amount) FROM sub_orders)
ORDER BY order_id;
```
The scalar aggregate subquery returns one value.
</details>

## 4. Customers Above A 75.00 Order

Return customers with an order over 75.00 using a correlated existence test.

**Expected result:** Asha only.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,c.name FROM sub_customers c
WHERE EXISTS (SELECT 1 FROM sub_orders o WHERE o.customer_id=c.customer_id AND o.amount>75)
ORDER BY c.customer_id;
```
Order 101 qualifies; Bharat's amount is exactly 75.00.
</details>

## 5. Highest Order Per Customer

Return each customer's highest order amount, including a NULL for customers with no orders.

**Expected result:** Asha 100.00, Bharat 75.00, Charu NULL.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,
 (SELECT MAX(o.amount) FROM sub_orders o WHERE o.customer_id=c.customer_id) AS highest_order
FROM sub_customers c ORDER BY c.customer_id;
```
The correlated scalar aggregate returns NULL for no matching rows.
</details>

## 6. Use A Derived Aggregate

Return customers whose total order amount exceeds 100.00.

**Expected result:** Asha with 150.00.

<details><summary>Show answer</summary>

```sql
SELECT totals.customer_id,totals.total_amount
FROM (SELECT customer_id,SUM(amount) AS total_amount FROM sub_orders
      WHERE customer_id IS NOT NULL GROUP BY customer_id) AS totals
WHERE totals.total_amount>100 ORDER BY totals.customer_id;
```
The derived table has one row per registered customer with orders.
</details>

## 7. Find Orders Matching Their Customer's Maximum

Return orders that equal the maximum order amount for their customer.

**Expected result:** Orders 101 and 103.

<details><summary>Show answer</summary>

```sql
SELECT o.order_id,o.customer_id,o.amount FROM sub_orders o
WHERE o.customer_id IS NOT NULL AND o.amount=(
 SELECT MAX(o2.amount) FROM sub_orders o2 WHERE o2.customer_id=o.customer_id
) ORDER BY o.customer_id,o.order_id;
```
Tied maximum orders would both be returned.
</details>

## 8. Debug NOT IN With NULL

Explain why `SELECT customer_id FROM sub_customers WHERE customer_id NOT IN (SELECT customer_id FROM sub_orders)` returns no rows. Write a safe anti-match.

**Expected result:** Customer 3 is the only customer without an order.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id FROM sub_customers c
WHERE NOT EXISTS (SELECT 1 FROM sub_orders o WHERE o.customer_id=c.customer_id)
ORDER BY c.customer_id;
```
The subquery includes NULL, making nonmatching comparisons UNKNOWN rather than TRUE.
</details>

## 9. Scalar Subquery Returns Multiple Rows

Why can `(SELECT amount FROM sub_orders WHERE status='paid')` not be used as a scalar comparison, and return the highest paid amount instead?

**Expected result:** The scalar value is 100.00.

<details><summary>Show answer</summary>

```sql
SELECT MAX(amount) AS highest_paid FROM sub_orders WHERE status='paid';
```
A scalar context requires at most one row; MAX reduces the matching rows to one result.
</details>

## 10. Avoid Duplicate Customers

A join to paid orders returns Asha once per paid order. Rewrite it so the output is one row per qualifying customer.

**Expected result:** Asha and Bharat each appear once.

<details><summary>Show answer</summary>

```sql
SELECT c.customer_id,c.name FROM sub_customers c
WHERE EXISTS (SELECT 1 FROM sub_orders o WHERE o.customer_id=c.customer_id AND o.status='paid')
ORDER BY c.customer_id;
```
EXISTS matches a condition rather than producing joined pairs.
</details>

## 11. Interview: EXISTS Or JOIN?

Explain the result-shape difference between EXISTS and an ordinary join.

**Expected result:** Mention existence semantics, duplicate matches, and that performance must be measured.

<details><summary>Show answer</summary>

EXISTS keeps an outer row when any match exists and does not multiply it by the number of matches. A join returns matching row pairs and may repeat the outer row. Neither form is universally faster; compare plans for the actual query.
</details>

## 12. Interview: Correlated Subquery

Define a correlated subquery and state one practical caution.

**Expected result:** Explain the outer reference and avoid claiming fixed execution/performance behavior.

<details><summary>Show answer</summary>

A correlated subquery refers to a value from the outer query, so its result is logically related to each outer row. The optimizer may transform it; use indexes appropriately and inspect the execution plan rather than assuming it runs slowly once per row.
</details>
