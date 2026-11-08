# Views And Stored Objects

[Exercises](19-views-stored-objects-exercises.md) | [Topic index](../start.md)

## Interview Answer

A view is a named SELECT that presents data from underlying tables; it is not generally a separately stored copy of the result. Stored procedures package server-side statements and can accept parameters, while functions return a value for use in expressions and have more restrictions. I use these objects when they clarify a stable database boundary, but keep business logic ownership and deployment/versioning easy to understand.

## Key Points

- A view can simplify repeated projections and restrict which columns/rows a consumer sees. Updates through views work only for certain simple view definitions; do not assume every view is updatable.
- MySQL has no native materialized view that automatically stores and refreshes a query result. Use a summary table with explicit refresh/consistency rules if needed.
- A stored procedure is invoked with CALL and can take IN/OUT/INOUT parameters. It can contain multiple statements and transaction-related logic, subject to routine characteristics and application design.
- A stored function returns a value and can appear in expressions. It has restrictions on statements and side effects compared with procedures.
- Triggers run automatically for supported row events such as INSERT, UPDATE, DELETE. They can enforce local rules or audit, but hidden side effects can surprise application developers and complicate bulk operations.
- DEFINER/INVOKER security affects whose privileges are used. Review definer accounts and permissions carefully, particularly across deployments.
- Events schedule server-side tasks; they require event scheduler configuration and operational ownership.
- Keep stored object definitions in version-controlled migrations and test them like application code.

## Minimal Example

```sql
CREATE VIEW active_customers AS
SELECT customer_id, name
FROM customers
WHERE status = 'active';
```

The view names a query; it does not automatically cache the active-customer rows. Changes to base tables affect later reads of the view.

## Common Traps

- A view can hide query complexity but does not automatically improve performance or security if permissions are broad.
- A view with joins/aggregates may not be updatable.
- Triggers can create unobserved writes or errors; document them and inspect them when debugging data changes.
- MySQL does not refresh a materialized view automatically because native materialized views are not supported.

## Likely Follow-Ups

**Procedure versus function?** Procedures are called with CALL and can perform a sequence of operations; functions return a value usable in expressions and have more restrictions.

**Why use a view?** To present a reusable projection or privilege boundary, while remembering that the underlying query still executes.

**Should all business logic be in stored procedures?** Not necessarily. Choose based on team ownership, deployment practices, portability, and the need for one shared database-side operation.

## MySQL References

Examples target MySQL 8.4. See [views](https://dev.mysql.com/doc/refman/8.4/en/views.html), [stored routines](https://dev.mysql.com/doc/refman/8.4/en/stored-routines.html), and [triggers](https://dev.mysql.com/doc/refman/8.4/en/triggers.html).
