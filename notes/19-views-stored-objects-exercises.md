# Views And Stored Objects: Exercises

[Notes](19-views-stored-objects.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 DDL/diagnostic tasks, and 2 interview questions. Run CREATE statements in a fresh MySQL 8.4 schema. Object privileges and definer behavior must be reviewed in the target deployment.

## 1. Reuse An Active-Customer Query

Create a view exposing IDs and names for active customers only.

**Expected result:** The view returns only active rows and only the selected columns.

<details><summary>Show answer</summary>

```sql
CREATE VIEW active_customers AS
SELECT customer_id,name FROM customers WHERE status='active';
```
The view stores a definition, not an automatic copy of result rows.
</details>

## 2. Restrict A Reporting Projection

A report user needs order IDs and totals but must not see customer email addresses. Propose a view and access pattern.

**Expected result:** Expose only required columns through a view and grant access to that view as supported by policy.

<details><summary>Show answer</summary>

```sql
CREATE VIEW order_report AS
SELECT order_id,customer_id,total_amount FROM orders;
```
Grant the reporting account only required SELECT access; verify underlying privilege/security behavior and avoid broad base-table grants.
</details>

## 3. Choose A Procedure For A Multi-Step Operation

A database-side operation accepts an account ID and returns a result status after several statements. Which stored object is a natural fit?

**Expected result:** A stored procedure with an IN parameter and an OUT result or result set.

<details><summary>Show answer</summary>

A procedure is called with CALL and supports IN/OUT/INOUT parameters. Define transaction ownership and error signaling clearly; it is not automatically safer than application code.
</details>

## 4. Choose A Function For A Scalar

A deterministic tax-band calculation returns one label from an amount. Which object shape could represent it, and what should be considered?

**Expected result:** A stored function returning a scalar, subject to restrictions and deployment/versioning.

<details><summary>Show answer</summary>

A stored function can return a scalar and be used in expressions, but it has restrictions on statements and side effects. Keep deterministic business rules consistent between application and database clients.
</details>

## 5. Audit A Row Change With A Trigger

A team proposes a trigger to insert an audit record after each order update. What should be reviewed?

**Expected result:** Hidden side effects, transaction/error behavior, bulk effects, permissions, and ownership.

<details><summary>Show answer</summary>

Confirm the audit requirement, failure semantics, data volume, recursion/side-effect risks, and how the trigger is versioned and tested. Trigger writes participate in the statement transaction and can cause the update to fail.
</details>

## 6. Need A Cached Monthly Summary

A dashboard's aggregate query is too slow. Does creating a view materialize it? Propose a design option.

**Expected result:** A normal view does not cache; use an explicitly maintained summary table if justified.

<details><summary>Show answer</summary>

A view executes its underlying query and is not a native materialized view in MySQL. A summary table can cache totals, but requires refresh/update, consistency, and rebuild rules.
</details>

## 7. Create A View

Write a view listing paid order IDs and amounts.

**Expected result:** The definition filters paid orders and returns only requested fields.

<details><summary>Show answer</summary>

```sql
CREATE VIEW paid_orders AS
SELECT order_id,amount FROM orders WHERE status='paid';
```
Subsequent SELECTs read current base-table data through the view definition.
</details>

## 8. Inspect A View Definition

Name one MySQL command to inspect a view definition and one to list views/tables.

**Expected result:** SHOW CREATE VIEW and SHOW FULL TABLES or information_schema.

<details><summary>Show answer</summary>

```sql
SHOW CREATE VIEW paid_orders;
SHOW FULL TABLES;
```
Use information_schema when a queryable metadata view is more appropriate.
</details>

## 9. Debug An Updatability Assumption

Can every view be updated? Give examples of features that can make a view non-updatable.

**Expected result:** No; aggregates, grouping, and some joins/derived constructs restrict updates.

<details><summary>Show answer</summary>

No. A view with GROUP BY/aggregate, UNION, or certain joins/derived expressions may not be updatable. Check MySQL's documented rules for the exact definition.
</details>

## 10. Review A DEFINER Account

A view was created by a developer account that no longer exists. What deployment concern should be reviewed?

**Expected result:** Definer security and privileges; use an intentional stable definer or INVOKER policy.

<details><summary>Show answer</summary>

Review whether the object uses SQL SECURITY DEFINER or INVOKER, which account is recorded as definer, and what privileges callers need. Manage the definer consistently through deployment migrations.
</details>

## 11. Interview: View Versus Table

Explain a normal view versus a stored table.

**Expected result:** A view is a query definition; a table stores rows; native materialization is absent.

<details><summary>Show answer</summary>

A normal view stores a SELECT definition and reads its underlying tables when queried; it does not store a separate result copy. A table stores rows. MySQL has no native auto-refreshing materialized view.
</details>

## 12. Interview: Procedure Versus Function

Compare their invocation and typical output.

**Expected result:** CALL/sequence versus scalar return, with function restrictions.

<details><summary>Show answer</summary>

A procedure is invoked with CALL and can perform a sequence of statements with parameters and result sets. A function returns a value usable in expressions and has more restrictions on statements and side effects.
</details>
