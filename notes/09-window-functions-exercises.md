# Window Functions: Exercises

[Notes](09-window-functions.md) | [Topic index](../start.md)

12 questions: 7 scenario queries, 3 debugging/edge cases, and 2 interview questions. Window functions require MySQL 8.0+. Salary ties are intentional; output order includes deterministic tie-breakers.

## Setup

```sql
CREATE TABLE window_sales (
 sale_id INT PRIMARY KEY, employee_id INT NOT NULL, department_id INT NOT NULL,
 sold_at DATE NOT NULL, amount DECIMAL(8,2) NOT NULL
);
INSERT INTO window_sales VALUES
 (1,10,1,'2026-01-01',100),(2,11,1,'2026-01-02',100),(3,12,1,'2026-01-03',80),
 (4,20,2,'2026-01-01',90),(5,21,2,'2026-01-02',70);
```

## 1. Number Department Employees

Return each sale with a row number per department, ordered by amount descending then sale ID.

**Expected result:** Department 1 ranks sale IDs 1, 2, 3; department 2 ranks 4, 5.

<details><summary>Show answer</summary>

```sql
SELECT sale_id,department_id,amount,
 ROW_NUMBER() OVER(PARTITION BY department_id ORDER BY amount DESC,sale_id) AS row_num
FROM window_sales ORDER BY department_id,row_num;
```
The primary key makes ordering deterministic.
</details>

## 2. Rank Salary Levels

Assign DENSE_RANK by amount within each department, highest first.

**Expected result:** Department 1 amounts 100 tie at rank 1 and 80 is rank 2; department 2 amounts rank 1 and 2.

<details><summary>Show answer</summary>

```sql
SELECT sale_id,department_id,amount,
 DENSE_RANK() OVER(PARTITION BY department_id ORDER BY amount DESC) AS amount_rank
FROM window_sales ORDER BY department_id,amount_rank,sale_id;
```
Tied amounts share a rank and later ranks have no gaps.
</details>

## 3. Return Top Salary Level Per Department

Return every sale tied at its department's highest amount.

**Expected result:** Sale IDs 1, 2, and 4.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT *,DENSE_RANK() OVER(PARTITION BY department_id ORDER BY amount DESC) AS r
 FROM window_sales
)
SELECT sale_id,department_id,amount FROM ranked WHERE r=1 ORDER BY department_id,sale_id;
```
DENSE_RANK retains all top ties.
</details>

## 4. Exactly One Latest Sale Per Department

Return the latest sale date per department, breaking same-date ties by highest sale ID.

**Expected result:** Sale 3 for department 1 and sale 5 for department 2.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY department_id ORDER BY sold_at DESC,sale_id DESC) AS rn
 FROM window_sales
)
SELECT sale_id,department_id,sold_at FROM ranked WHERE rn=1 ORDER BY department_id;
```
ROW_NUMBER with a unique tie-breaker picks one deterministic row.
</details>

## 5. Calculate A Running Sales Total

Return each department's cumulative amount by sale ID.

**Expected result:** Department 1 totals 100.00, 200.00, 280.00; department 2 totals 90.00, 160.00.

<details><summary>Show answer</summary>

```sql
SELECT sale_id,department_id,amount,
 SUM(amount) OVER(PARTITION BY department_id ORDER BY sale_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM window_sales ORDER BY department_id,sale_id;
```
The explicit ROWS frame defines row-by-row accumulation.
</details>

## 6. Compare Sale To Previous Sale

Return each sale and the previous sale amount in its department, ordered by sale ID.

**Expected result:** The first sale in each department has NULL previous amount; subsequent rows see the prior ID's amount.

<details><summary>Show answer</summary>

```sql
SELECT sale_id,department_id,amount,
 LAG(amount) OVER(PARTITION BY department_id ORDER BY sale_id) AS prior_amount
FROM window_sales ORDER BY department_id,sale_id;
```
LAG returns NULL when there is no preceding row unless a default is supplied.
</details>

## 7. Find Sales Above Department Average

Return sales above their department's average amount.

**Expected result:** Return sales 1, 2, and 4: the two 100.00 sales are above department 1's 93.33 average, and the 90.00 sale is above department 2's 80.00 average.

<details><summary>Show answer</summary>

```sql
WITH measured AS (
 SELECT *,AVG(amount) OVER(PARTITION BY department_id) AS dept_avg FROM window_sales
)
SELECT sale_id,department_id,amount FROM measured WHERE amount>dept_avg ORDER BY department_id,sale_id;
```
Expected rows are sales 1, 2, and 4. The window average leaves each sale row available.
</details>

## 8. Debug Window Alias In WHERE

Why is `SELECT ..., ROW_NUMBER() OVER(...) AS rn FROM window_sales WHERE rn=1` invalid? Correct it.

**Expected result:** Use a CTE/derived table and return one first row per department.

<details><summary>Show answer</summary>

```sql
WITH ranked AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY department_id ORDER BY sale_id) AS rn FROM window_sales
)
SELECT sale_id,department_id FROM ranked WHERE rn=1 ORDER BY department_id;
```
WHERE is evaluated before the window result is available; MySQL has no QUALIFY clause.
</details>

## 9. Debug Top Two Rows Versus Rank Values

If `DENSE_RANK() <= 2` returns three employees, is that a bug?

**Expected result:** No; ties can produce more than two rows across two rank levels.

<details><summary>Show answer</summary>

No. DENSE_RANK selects two distinct value levels and retains every tie. Use ROW_NUMBER with a deterministic tie-breaker when exactly two rows are required.
</details>

## 10. Debug A Running Total With Ties

Why can the default frame give peer rows the same cumulative total? How do you request row-by-row totals?

**Expected result:** Use an explicit ROWS frame and deterministic order.

<details><summary>Show answer</summary>

```sql
SUM(amount) OVER(ORDER BY sold_at,sale_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```
An explicit ROWS frame and unique ordering define accumulation one row at a time.
</details>

## 11. Interview: RANK Versus GROUP BY

How does a window calculation differ from grouping?

**Expected result:** Explain preserved input rows versus collapsed groups.

<details><summary>Show answer</summary>

GROUP BY produces one row per group (or aggregate group), while a window function calculates over related rows and keeps the original row-level results. Use the latter when each record needs a group total or rank alongside it.
</details>

## 12. Interview: ROW_NUMBER Or DENSE_RANK?

Which should you use for exactly N rows versus top N distinct values?

**Expected result:** Explain deterministic row selection versus tie-aware distinct levels.

<details><summary>Show answer</summary>

Use ROW_NUMBER with a unique tie-breaker to select at most N rows. Use DENSE_RANK when N means distinct value levels and all ties at those levels should remain.
</details>
