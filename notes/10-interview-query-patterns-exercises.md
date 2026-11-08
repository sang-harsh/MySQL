# Interview Query Patterns: Exercises

[Notes](10-interview-query-patterns.md) | [Topic index](../start.md)

12 questions: 7 query-writing tasks, 3 debugging/edge cases, and 2 interview questions. Use an isolated MySQL 8.4 schema. Ties are retained unless a task asks for exactly N rows; all outputs have explicit ordering.

## Setup

```sql
CREATE TABLE pattern_employees (
 employee_id INT PRIMARY KEY, name VARCHAR(40) NOT NULL,
 department_id INT NOT NULL, salary DECIMAL(10,2) NOT NULL
);
CREATE TABLE pattern_orders (
 order_id INT PRIMARY KEY, customer_id INT NOT NULL,
 ordered_at DATETIME NOT NULL, amount DECIMAL(8,2) NOT NULL
);
CREATE TABLE pattern_users (user_id INT PRIMARY KEY, email VARCHAR(100) NOT NULL);
INSERT INTO pattern_employees VALUES
 (1,'Asha',10,90000),(2,'Bharat',10,80000),(3,'Charu',10,80000),
 (4,'Dev',20,70000),(5,'Esha',20,60000),(6,'Farah',20,60000);
INSERT INTO pattern_orders VALUES
 (101,1,'2026-03-01 10:00:00',20),(102,1,'2026-03-01 10:00:00',30),
 (103,2,'2026-03-02 10:00:00',15);
INSERT INTO pattern_users VALUES (1,'a@example.test'),(2,'b@example.test'),(3,'a@example.test');
```

## 1. Second Distinct Salary

Return the second-highest distinct salary.

**Expected result:** 80000.00.

<details><summary>Show answer</summary>

```sql
SELECT DISTINCT salary FROM pattern_employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
```
DISTINCT makes this the second salary level, not the second employee.
</details>

## 2. Find Duplicate Emails

Return each duplicated email and its row count.

**Expected result:** `a@example.test`, count 2.

<details><summary>Show answer</summary>

```sql
SELECT email,COUNT(*) AS row_count FROM pattern_users
GROUP BY email HAVING COUNT(*)>1 ORDER BY email;
```
Group by the business key and retain groups with multiple records.
</details>

## 3. Latest Order Per Customer, Including Ties

Return all orders at each customer's latest timestamp.

**Expected result:** Orders 101 and 102 for customer 1; order 103 for customer 2.

<details><summary>Show answer</summary>

```sql
SELECT o.order_id,o.customer_id,o.ordered_at FROM pattern_orders o
WHERE o.ordered_at=(SELECT MAX(o2.ordered_at) FROM pattern_orders o2 WHERE o2.customer_id=o.customer_id)
ORDER BY o.customer_id,o.order_id;
```
Equality to MAX retains all rows tied at the latest timestamp.
</details>

## 4. Top Two Salary Levels Per Department

Return every employee whose salary is in the department's top two distinct salary levels.

**Expected result:** Department 10 returns Asha, Bharat, Charu; department 20 returns Dev, Esha, Farah.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT employee_id,name,department_id,salary,
 DENSE_RANK() OVER(PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
 FROM pattern_employees
)
SELECT employee_id,name,department_id,salary FROM ranked WHERE salary_rank<=2
ORDER BY department_id,salary DESC,employee_id;
```
DENSE_RANK retains salary ties and counts distinct salary levels.
</details>

## 5. Employees Above The Company Average

Return employees paid more than the overall average.

**Expected result:** Asha only.

<details><summary>Show answer</summary>

```sql
SELECT employee_id,name,salary FROM pattern_employees
WHERE salary>(SELECT AVG(salary) FROM pattern_employees) ORDER BY employee_id;
```
The average is 75000.00.
</details>

## 6. Exactly Two Employees Per Department

Return at most two employees per department, selecting highest salary then lowest employee ID.

**Expected result:** IDs 1 and 2 for department 10; IDs 4 and 5 for department 20.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT employee_id,department_id,salary,
 ROW_NUMBER() OVER(PARTITION BY department_id ORDER BY salary DESC,employee_id) AS row_num
 FROM pattern_employees
)
SELECT employee_id,department_id,salary FROM ranked WHERE row_num<=2
ORDER BY department_id,row_num;
```
ROW_NUMBER with a unique tie-breaker gives exactly N rows when the group has enough rows.
</details>

## 7. Total Order Amount Per Customer

Show every customer ID that has orders and its total amount.

**Expected result:** Customer 1 has 50.00; customer 2 has 15.00.

<details><summary>Show answer</summary>

```sql
SELECT customer_id,SUM(amount) AS total_amount FROM pattern_orders
GROUP BY customer_id ORDER BY customer_id;
```
Aggregate at customer grain.
</details>

## 8. Debug Second-Highest Salary

Why can `ORDER BY salary DESC LIMIT 1 OFFSET 1` return 80000 rather than a distinct second salary when employees tie? Correct it.

**Expected result:** Return 80000.00 as the second distinct salary.

<details><summary>Show answer</summary>

```sql
SELECT DISTINCT salary FROM pattern_employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
```
Without DISTINCT the query selects a row, not a salary level.
</details>

## 9. Debug Latest Order Selection

Why can `SELECT customer_id,MAX(ordered_at),order_id FROM pattern_orders GROUP BY customer_id` fail in strict mode or return an unreliable ID? Give a deterministic single-latest-row query.

**Expected result:** Customer 1 selects order 102 and customer 2 selects order 103 using order ID as the tie-breaker.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT order_id,customer_id,ordered_at,
 ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY ordered_at DESC,order_id DESC) AS rn
 FROM pattern_orders
)
SELECT order_id,customer_id,ordered_at FROM ranked WHERE rn=1 ORDER BY customer_id;
```
The ID is not functionally determined by the grouped customer and maximum time; ranking defines tie behavior.
</details>

## 10. Preview Duplicate Rows Before Removal

Write a SELECT that returns the larger user ID for each duplicate email, keeping the smallest ID. Do not delete rows.

**Expected result:** Only user ID 3 is selected.

<details><summary>Show answer</summary>

```sql
SELECT newer.user_id,newer.email FROM pattern_users newer
JOIN pattern_users older ON older.email=newer.email AND older.user_id<newer.user_id
GROUP BY newer.user_id,newer.email ORDER BY newer.user_id;
```
This is a review preview only; deletion requires an explicit preservation policy and safe transaction.
</details>

## 11. Interview: RANK Functions

Compare ROW_NUMBER, RANK, and DENSE_RANK for equal salaries.

**Expected result:** Explain ties and gaps in rank values.

<details><summary>Show answer</summary>

ROW_NUMBER assigns a unique sequence even for ties. RANK gives tied rows the same rank and leaves gaps afterward; DENSE_RANK gives tied rows the same rank without gaps. Use DENSE_RANK for distinct salary levels and ROW_NUMBER for a fixed number of deterministically selected rows.
</details>

## 12. Interview: Clarify “Second Highest”

What clarification should you ask before writing a second-highest-value query?

**Expected result:** Distinguish second row from second distinct value and state tie behavior.

<details><summary>Show answer</summary>

Ask whether “second” means the second row after sorting or the second distinct value, and whether all ties should be returned. Then choose row numbering or distinct values/DENSE_RANK and define a stable tie-breaker if one row is required.
</details>
