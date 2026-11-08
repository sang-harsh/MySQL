# Aggregation And Conditional Reporting: Exercises

[Notes](05-aggregation-reporting.md) | [Topic index](../start.md)

12 questions: 7 reporting queries, 3 debugging/edge cases, and 2 interview questions. Use an isolated MySQL 8.4 practice schema; all dates are fixed and results require explicit ordering.

## Setup

```sql
CREATE TABLE report_customers (customer_id INT PRIMARY KEY, name VARCHAR(40) NOT NULL);
CREATE TABLE report_orders (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  status VARCHAR(16) NOT NULL,
  amount DECIMAL(8,2) NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES report_customers(customer_id)
);
CREATE TABLE report_payments (
  payment_id INT PRIMARY KEY,
  order_id INT NOT NULL,
  amount DECIMAL(8,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES report_orders(order_id)
);
INSERT INTO report_customers VALUES (1,'Asha'),(2,'Bharat'),(3,'Charu');
INSERT INTO report_orders VALUES
 (101,1,'paid',100),(102,1,'pending',50),(103,2,'paid',75);
INSERT INTO report_payments VALUES (501,101,60),(502,101,40),(503,103,75);
```

Each customer's order amount is counted once; order 101 has two payments. Unless specified, sort by customer ID. Questions are independent.

## 1. Count Orders Per Customer

Show each customer with their order count, including customers with none.

**Expected result:** Asha 2, Bharat 1, Charu 0.

<details>
<summary>Show answer</summary>

```sql
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM report_customers AS c LEFT JOIN report_orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name ORDER BY c.customer_id;
```
Charu's NULL-extended row is excluded by `COUNT(o.order_id)`.
</details>

## 2. Sum Orders By Customer

Return each customer represented by at least one order and their total order amount.

**Expected result:** Asha 150.00; Bharat 75.00.

<details>
<summary>Show answer</summary>

```sql
SELECT customer_id, SUM(amount) AS order_total FROM report_orders
GROUP BY customer_id ORDER BY customer_id;
```
Grouping the fact table yields no row for Charu.
</details>

## 3. Count Only Paid Orders

Return each customer and their paid-order count, retaining customers with zero paid orders.

**Expected result:** Counts are 1, 1, and 0 for customers 1, 2, and 3.

<details>
<summary>Show answer</summary>

```sql
SELECT c.customer_id, COUNT(CASE WHEN o.status = 'paid' THEN o.order_id END) AS paid_count
FROM report_customers AS c LEFT JOIN report_orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id ORDER BY c.customer_id;
```
CASE returns NULL for non-paid rows, which COUNT ignores.
</details>

## 4. Show Paid And Pending Totals

Return one row per customer with paid and pending order totals, including zero totals.

**Expected result:** Asha 100.00 and 50.00; Bharat 75.00 and 0.00; Charu 0.00 and 0.00.

<details>
<summary>Show answer</summary>

```sql
SELECT c.customer_id,
 SUM(CASE WHEN o.status='paid' THEN o.amount ELSE 0 END) AS paid_total,
 SUM(CASE WHEN o.status='pending' THEN o.amount ELSE 0 END) AS pending_total
FROM report_customers AS c LEFT JOIN report_orders AS o ON o.customer_id=c.customer_id
GROUP BY c.customer_id ORDER BY c.customer_id;
```
ELSE 0 keeps the no-order group at zero.
</details>

## 5. Find Customers With Multiple Orders

Return customers with at least two orders and their counts.

**Expected result:** Only customer 1, with count 2.

<details>
<summary>Show answer</summary>

```sql
SELECT customer_id, COUNT(*) AS order_count FROM report_orders
GROUP BY customer_id HAVING COUNT(*) >= 2 ORDER BY customer_id;
```
HAVING filters groups after aggregation.
</details>

## 6. Average Order Value By Status

Return each status and its average order amount, rounded to two decimals.

**Expected result:** paid 87.50; pending 50.00.

<details>
<summary>Show answer</summary>

```sql
SELECT status, ROUND(AVG(amount), 2) AS average_amount FROM report_orders
GROUP BY status ORDER BY status;
```
There are two paid orders, so their average is 87.50.
</details>

## 7. Total Payments Per Customer Without Inflating Order Totals

Show each registered customer and the sum of their payment amounts.

**Expected result:** Asha 100.00, Bharat 75.00, Charu 0.00.

<details>
<summary>Show answer</summary>

```sql
SELECT c.customer_id, COALESCE(SUM(p.amount), 0.00) AS payment_total
FROM report_customers AS c
LEFT JOIN report_orders AS o ON o.customer_id=c.customer_id
LEFT JOIN report_payments AS p ON p.order_id=o.order_id
GROUP BY c.customer_id ORDER BY c.customer_id;
```
This query sums payments only; never sum order amounts in the same joined result because multiple payments repeat an order.
</details>

## 8. Debug WHERE With An Aggregate

Why does `SELECT customer_id, SUM(amount) FROM report_orders WHERE SUM(amount) > 100 GROUP BY customer_id` fail? Correct it.

**Expected result:** It returns Asha with 150.00.

<details>
<summary>Show answer</summary>

```sql
SELECT customer_id, SUM(amount) AS total FROM report_orders
GROUP BY customer_id HAVING SUM(amount) > 100 ORDER BY customer_id;
```
WHERE cannot use a group aggregate; HAVING evaluates after grouping.
</details>

## 9. Debug The Empty-Customer Count

Why does this query show Charu with a count of 1? Correct it: `SELECT c.customer_id, COUNT(*) FROM report_customers c LEFT JOIN report_orders o ON o.customer_id=c.customer_id GROUP BY c.customer_id`.

**Expected result:** Counts are 2, 1, 0.

<details>
<summary>Show answer</summary>

```sql
SELECT c.customer_id, COUNT(o.order_id) AS order_count
FROM report_customers AS c LEFT JOIN report_orders AS o ON o.customer_id=c.customer_id
GROUP BY c.customer_id ORDER BY c.customer_id;
```
COUNT(*) counts the placeholder row; counting the non-NULL child key counts matches only.
</details>

## 10. Detect Join Inflation

What total would `SUM(o.amount)` produce after joining orders to payments, and how should the order total be obtained correctly?

**Expected result:** The joined sum is 275.00 because order 101 is repeated; the correct order total is 225.00.

<details>
<summary>Show answer</summary>

```sql
SELECT SUM(amount) AS order_total FROM report_orders;
```
Aggregate at order grain before joining payment rows, or calculate order and payment aggregates separately. DISTINCT on amount is not a valid general fix.
</details>

## 11. Interview: COUNT Variants

Explain the difference among COUNT(*), COUNT(column), and COUNT(DISTINCT column).

**Expected result:** Cover rows, NULL handling, and duplicate handling.

<details>
<summary>Show answer</summary>

`COUNT(*)` counts result rows, including rows whose columns are NULL. `COUNT(column)` counts only non-NULL values. `COUNT(DISTINCT column)` counts distinct non-NULL values.
</details>

## 12. Interview: WHERE Or HAVING?

Explain when to use WHERE and HAVING.

**Expected result:** State the logical point of filtering and give an aggregate-threshold example.

<details>
<summary>Show answer</summary>

WHERE filters input rows before grouping; HAVING filters groups after aggregation, such as `HAVING COUNT(*) >= 2`. Prefer WHERE for nonaggregate predicates so fewer rows need grouping.
</details>
