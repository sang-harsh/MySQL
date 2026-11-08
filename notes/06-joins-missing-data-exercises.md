# Joins And Missing-Data Queries: Exercises

[Notes](06-joins-missing-data.md) | [Topic index](../start.md)

12 questions: 7 scenario-based query tasks, 3 debugging/edge-case tasks, and 2 interview questions. Difficulty: quick to medium. Attempt each question before reading its answer.

## Shared Setup And Rules

Run this setup once in a new, isolated practice schema of your choice, never an application database. It creates only `join_` practice tables; it does not drop or overwrite existing tables. To repeat, use a fresh practice schema. Target MySQL 8.4 LTS/InnoDB with strict SQL mode and ONLY_FULL_GROUP_BY.

All IDs are primary keys. An order has zero or one registered customer; NULL means a guest checkout, not an invalid foreign key. Customers can have multiple orders; orders can have multiple payment installments. Employee managers are optional and self-referencing. Monetary values are INR. Questions are independent SELECTs and do not mutate the fixture.

Dates are fixed UTC DATETIME values. No date conversion is needed here. Order by the stated IDs, not names; there is no implicit row ordering or tie-breaking by amount. SQL NULL is shown as NULL in results.

```sql
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY,NO_ENGINE_SUBSTITUTION';
SET SESSION time_zone = '+00:00';

CREATE TABLE join_customers (
  customer_id INT PRIMARY KEY,
  name VARCHAR(40) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE join_orders (
  order_id INT PRIMARY KEY,
  customer_id INT NULL,
  status VARCHAR(16) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  ordered_at DATETIME NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES join_customers(customer_id)
) ENGINE=InnoDB;

CREATE TABLE join_payments (
  payment_id INT PRIMARY KEY,
  order_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES join_orders(order_id)
) ENGINE=InnoDB;

CREATE TABLE join_employees (
  employee_id INT PRIMARY KEY,
  name VARCHAR(40) NOT NULL,
  manager_id INT NULL,
  FOREIGN KEY (manager_id) REFERENCES join_employees(employee_id)
) ENGINE=InnoDB;

CREATE TABLE join_products (
  product_id INT PRIMARY KEY,
  name VARCHAR(40) NOT NULL
) ENGINE=InnoDB;

INSERT INTO join_customers VALUES
  (1, 'Asha'), (2, 'Bharat'), (3, 'Charu'), (4, 'Dev');
INSERT INTO join_orders VALUES
  (101, 1, 'paid', 100.00, '2026-01-31 23:59:59'),
  (102, 1, 'pending', 50.00, '2026-02-01 00:00:00'),
  (103, 2, 'paid', 75.00, '2026-02-02 10:00:00'),
  (104, NULL, 'paid', 20.00, '2026-02-03 10:00:00');
INSERT INTO join_payments VALUES
  (501, 101, 60.00), (502, 101, 40.00), (503, 103, 75.00);
INSERT INTO join_employees VALUES (1, 'Mira', NULL);
INSERT INTO join_employees VALUES (2, 'Neel', 1), (3, 'Sara', 1);
INSERT INTO join_employees VALUES (4, 'Tara', 2);
INSERT INTO join_products VALUES (201, 'Keyboard'), (202, 'Mouse');
```

Fixture summary: Asha has two orders, Bharat has one, Charu and Dev have none. Order 104 is a guest order. Order 101 has two payments, order 103 has one, and orders 102/104 have none. Mira has no manager; Neel and Sara report to Mira; Tara reports to Neel. There are four customers and two products.

## 1. List Orders With Registered Customer Names (Quick)

Write a query that shows the order ID, customer name, and order amount for every order placed by a registered customer. Include pending orders, but exclude guest orders. Sort the results by order ID.

**Expected result:** Return three rows: Asha's orders 101 and 102, with amounts 100.00 and 50.00, and Bharat's order 103, with amount 75.00. Do not return guest order 104.

<details>
<summary>Show answer</summary>


```sql
SELECT orders.order_id, customers.name, orders.amount
FROM join_orders AS orders
INNER JOIN join_customers AS customers
  ON customers.customer_id = orders.customer_id
ORDER BY orders.order_id;
```

```text
order_id | name   | amount
101      | Asha   | 100.00
102      | Asha   | 50.00
103      | Bharat | 75.00
```

INNER JOIN keeps matched pairs only. Asha legitimately appears twice; the guest's NULL customer ID matches no customer.

</details>

## 2. List Every Customer And Their Orders (Quick)

Write a query that shows each customer's ID, name, and order IDs. Include customers who have not placed any orders. Sort the results by customer ID, then by order ID.

**Expected result:** Return five rows. Asha appears twice, for orders 101 and 102. Bharat appears once, for order 103. Charu and Dev each appear once with a NULL order ID.

<details>
<summary>Show answer</summary>


```sql
SELECT customers.customer_id, customers.name, orders.order_id
FROM join_customers AS customers
LEFT JOIN join_orders AS orders
  ON orders.customer_id = customers.customer_id
ORDER BY customers.customer_id, orders.order_id;
```

```text
customer_id | name   | order_id
1           | Asha   | 101
1           | Asha   | 102
2           | Bharat | 103
3           | Charu  | NULL
4           | Dev    | NULL
```

LEFT JOIN preserves every customer and creates a NULL-extended row for a missing order. It does not promise one output row per customer when multiple orders match.

</details>

## 3. Find Customers Who Have Never Ordered (Quick)

Write a query that shows the IDs and names of registered customers who have never placed an order. An order counts regardless of its status. Sort the results by customer ID.

**Expected result:** Return two rows: customer 3, Charu, and customer 4, Dev. A guest order does not count as an order for either customer.

<details>
<summary>Show answer</summary>


```sql
SELECT customers.customer_id, customers.name
FROM join_customers AS customers
LEFT JOIN join_orders AS orders
  ON orders.customer_id = customers.customer_id
WHERE orders.order_id IS NULL
ORDER BY customers.customer_id;
```

```text
customer_id | name
3           | Charu
4           | Dev
```

The non-nullable order primary key identifies a missing match reliably. Testing a nullable business field could incorrectly classify an existing order as absent.

</details>

## 4. Attach Paid Orders Without Losing Customers (Medium)

Write a query that shows every customer's ID and name, together with the IDs of their paid orders. Keep customers who have no paid orders, including customers who have only pending orders. Sort the results by customer ID, then by order ID.

**Expected result:** Return four rows. Asha has order 101, and Bharat has order 103. Charu and Dev have NULL order IDs. Do not show pending order 102.

<details>
<summary>Show answer</summary>


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

The status filter belongs in ON because it defines eligible matches, not which customers survive. If a customer has several paid orders, all of those pairs appear.

</details>

## 5. Show Employees And Their Managers (Quick)

Write a query that shows each employee's ID, name, and manager's name. Include employees who do not have a manager. Sort the results by employee ID.

**Expected result:** Return four rows. Mira's manager is NULL. Neel and Sara have Mira as their manager. Tara has Neel as her manager.

<details>
<summary>Show answer</summary>


```sql
SELECT employees.employee_id, employees.name, managers.name AS manager_name
FROM join_employees AS employees
LEFT JOIN join_employees AS managers
  ON managers.employee_id = employees.manager_id
ORDER BY employees.employee_id;
```

```text
employee_id | name | manager_name
1           | Mira | NULL
2           | Neel | Mira
3           | Sara | Mira
4           | Tara | Neel
```

This is a self join: aliases represent two roles of the same table. LEFT JOIN retains Mira; an INNER self join would omit her.

</details>

## 6. Generate Customer-Product Offer Pairs (Quick)

Every registered customer can receive an offer for every product. Write a query that lists every possible customer ID and product ID combination, regardless of whether the customer has ordered. Sort the results by customer ID, then by product ID.

**Expected result:** Return eight rows. Each of the four customers must appear once with product 201 and once with product 202.

<details>
<summary>Show answer</summary>


```sql
SELECT customers.customer_id, products.product_id
FROM join_customers AS customers
CROSS JOIN join_products AS products
ORDER BY customers.customer_id, products.product_id;
```

```text
customer_id | product_id
1           | 201
1           | 202
2           | 201
2           | 202
3           | 201
3           | 202
4           | 201
4           | 202
```

CROSS JOIN generates combinations without a matching condition. If either table is empty, the result is empty; on large tables, check the product of the row counts first.

</details>

## 7. Reconcile All Customers And All Orders (Medium)

Write a query that lists customer IDs and order IDs for all customers and all orders. Include matching customer-order pairs, customers without orders, and orders without a registered customer. Keep valid repeated customer IDs when a customer has multiple orders. Sort registered customers by customer ID, put guest rows last, and sort each customer's orders by order ID.

**Expected result:** Return six rows. Customer 1 has orders 101 and 102, customer 2 has order 103, and customers 3 and 4 each have a NULL order ID. The final row has a NULL customer ID and order ID 104.

<details>
<summary>Show answer</summary>


```sql
SELECT combined.customer_id, combined.order_id
FROM (
  SELECT customers.customer_id, orders.order_id
  FROM join_customers AS customers
  LEFT JOIN join_orders AS orders
    ON orders.customer_id = customers.customer_id
  UNION ALL
  SELECT customers.customer_id, orders.order_id
  FROM join_orders AS orders
  LEFT JOIN join_customers AS customers
    ON customers.customer_id = orders.customer_id
  WHERE customers.customer_id IS NULL
) AS combined
ORDER BY combined.customer_id IS NULL, combined.customer_id, combined.order_id;
```

```text
customer_id | order_id
1           | 101
1           | 102
2           | 103
3           | NULL
4           | NULL
NULL        | 104
```

MySQL has no native FULL OUTER JOIN. The second branch adds only unmatched orders, so UNION ALL preserves valid duplicates without repeating the matched pairs.

</details>

## 8. Debug A LEFT JOIN That Drops Customers (Medium)

The query below should list every registered customer's ID and the IDs of their paid orders. Customers without paid orders must still appear. Explain what the query currently returns, then correct it. Sort the results by customer ID, then by order ID.

**Expected result:** The corrected query must return four rows: customer 1 with order 101, customer 2 with order 103, and customers 3 and 4 with NULL order IDs. Customers who have only pending orders must also remain in the result.

**Query to fix:**

```sql
SELECT customers.customer_id, orders.order_id
FROM join_customers AS customers
LEFT JOIN join_orders AS orders
  ON orders.customer_id = customers.customer_id
WHERE orders.status = 'paid'
ORDER BY customers.customer_id, orders.order_id;
```

<details>
<summary>Show answer</summary>

**Current query output:**

```text
customer_id | order_id
1           | 101
2           | 103
```

**Corrected query:**

```sql
SELECT customers.customer_id, orders.order_id
FROM join_customers AS customers
LEFT JOIN join_orders AS orders
  ON orders.customer_id = customers.customer_id
 AND orders.status = 'paid'
ORDER BY customers.customer_id, orders.order_id;
```

```text
customer_id | order_id
1           | 101
2           | 103
3           | NULL
4           | NULL
```

WHERE rejects NULL-extended rows because NULL = 'paid' is unknown, not true. Adding `OR orders.order_id IS NULL` in WHERE is not a general fix: a customer with only pending orders would still disappear.

</details>

## 9. Debug Inflated Order Totals After Joining Payments (Medium)

The query below should return one row for each registered customer who has placed an order. Each row must show the customer ID, the total order amount, and the total payment amount. Explain why the query gives an incorrect order total, then correct it. Sort the results by customer ID.

**Expected result:** The corrected query must return two rows. Customer 1, Asha, has a total order amount of 150.00 and a total payment amount of 100.00. Customer 2, Bharat, has 75.00 for both totals.

**Query to fix:**

```sql
SELECT orders.customer_id, SUM(orders.amount) AS ordered_amount,
       SUM(payments.amount) AS paid_amount
FROM join_orders AS orders
LEFT JOIN join_payments AS payments ON payments.order_id = orders.order_id
WHERE orders.customer_id IS NOT NULL
GROUP BY orders.customer_id
ORDER BY orders.customer_id;
```

<details>
<summary>Show answer</summary>

**Current query output:**

```text
customer_id | ordered_amount | paid_amount
1           | 250.00         | 100.00
2           | 75.00          | 75.00
```

**Corrected query:**

```sql
SELECT orders.customer_id, SUM(orders.amount) AS ordered_amount,
       SUM(COALESCE(payment_totals.paid_amount, 0)) AS paid_amount
FROM join_orders AS orders
LEFT JOIN (
  SELECT order_id, SUM(amount) AS paid_amount
  FROM join_payments
  GROUP BY order_id
) AS payment_totals ON payment_totals.order_id = orders.order_id
WHERE orders.customer_id IS NOT NULL
GROUP BY orders.customer_id
ORDER BY orders.customer_id;
```

```text
customer_id | ordered_amount | paid_amount
1           | 150.00         | 100.00
2           | 75.00          | 75.00
```

Order 101 repeats once per payment in the direct join, so its amount is counted twice. Aggregate payments to one row per order first; SUM(DISTINCT orders.amount) is unsafe because different orders can have the same amount. COALESCE makes unpaid orders contribute zero payments.

</details>

## 10. Debug NOT IN When Guest Orders Exist (Medium)

The query below should show the IDs and names of registered customers who have never placed an order. Explain what happens when an order has a NULL customer ID, then correct the query so guest orders do not affect the result. Sort the results by customer ID.

**Expected result:** The corrected query must return two rows: customer 3, Charu, and customer 4, Dev. Guest order 104 must not prevent these customers from appearing.

**Query to fix:**

```sql
SELECT customers.customer_id, customers.name
FROM join_customers AS customers
WHERE customers.customer_id NOT IN (SELECT customer_id FROM join_orders)
ORDER BY customers.customer_id;
```

<details>
<summary>Show answer</summary>

**Current query output:**

```text
customer_id | name
(no rows)
```

**Corrected query:**

```sql
SELECT customers.customer_id, customers.name
FROM join_customers AS customers
WHERE NOT EXISTS (
  SELECT 1 FROM join_orders AS orders
  WHERE orders.customer_id = customers.customer_id
)
ORDER BY customers.customer_id;
```

```text
customer_id | name
3           | Charu
4           | Dev
```

For IDs absent from the non-NULL list, NOT IN with NULL evaluates to unknown, so WHERE rejects them. NOT EXISTS checks for actual matches and remains correct with guest rows; the LEFT anti-join in question 3 also works.

</details>

## 11. Explain RIGHT JOIN Versus LEFT JOIN (Quick Interview)

An interviewer asks you to list all customers, including those without orders. Explain the difference between RIGHT JOIN and LEFT JOIN, and say whether RIGHT JOIN is required for this task. Show a query that returns each customer's ID, name, and order IDs. Sort the results by customer ID, then by order ID.

**Expected result:** Explain which side each join preserves and whether swapping the tables gives the same result. Your query must return five rows: Asha with orders 101 and 102, Bharat with order 103, and Charu and Dev with NULL order IDs.

<details>
<summary>Show answer</summary>


A RIGHT JOIN keeps every row from its right-hand table, while a LEFT JOIN keeps every row from its left-hand table. Swapping the tables gives the same matching and missing-row behavior. I usually write LEFT JOIN with the table I want to preserve first because it makes the query easier to read.

```sql
SELECT customers.customer_id, customers.name, orders.order_id
FROM join_orders AS orders
RIGHT JOIN join_customers AS customers
  ON customers.customer_id = orders.customer_id
ORDER BY customers.customer_id, orders.order_id;
```

```text
customer_id | name   | order_id
1           | Asha   | 101
1           | Asha   | 102
2           | Bharat | 103
3           | Charu  | NULL
4           | Dev    | NULL
```

This is equivalent to question 2, including Asha's repeated customer row. RIGHT JOIN is supported in MySQL; it is not a performance guarantee.

</details>

## 12. Explain Why A Customer Repeats After A Join (Quick Interview)

You need a list of customers who have placed at least one order, not a list of their individual orders. Explain why Asha appears twice when customers are joined to orders. Write a query that returns each customer's ID and name only once without using DISTINCT. Sort the results by customer ID.

**Expected result:** Explain why one customer can produce multiple joined rows. Your query must return two rows: customer 1, Asha, and customer 2, Bharat. Asha must appear only once.

<details>
<summary>Show answer</summary>


A join returns matching pairs, not automatically one row per parent. Asha has two orders, so two customer-order pairs are correct. When I only need to know whether a customer has any order, EXISTS expresses that requirement directly and avoids creating multiple output rows for the customer.

```sql
SELECT customers.customer_id, customers.name
FROM join_customers AS customers
WHERE EXISTS (
  SELECT 1 FROM join_orders AS orders
  WHERE orders.customer_id = customers.customer_id
)
ORDER BY customers.customer_id;
```

```text
customer_id | name
1           | Asha
2           | Bharat
```

This returns each customer once regardless of order count. Guest orders do not match a registered customer, and an empty orders table produces no rows.

</details>

## References And Validation

[MySQL 8.4 JOIN syntax](https://dev.mysql.com/doc/refman/8.4/en/join.html) | [outer join simplification](https://dev.mysql.com/doc/refman/8.4/en/outer-join-simplification.html) | [IN/NOT IN comparisons](https://dev.mysql.com/doc/refman/8.4/en/comparison-operators.html#function_in)

These queries avoid MySQL 8-only features and also apply to 5.7/8.0. Content checks passed: 12 complete questions, shared fixture/key consistency, deterministic expected results, scenario coverage, and navigation. All 15 exercise query outputs and the note example were cross-checked in SQLite 3.50.4 using an in-memory fixture with foreign keys enabled; MySQL-only session settings and ENGINE clauses were excluded from that cross-check. MySQL execution, strict-mode behavior, and InnoDB-specific setup remain unverified; they require authorized practice-instance access.