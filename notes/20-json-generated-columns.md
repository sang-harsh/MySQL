# JSON And Generated Columns

[Exercises](20-json-generated-columns-exercises.md) | [Topic index](../start.md)

## Interview Answer

MySQL's JSON type validates and stores JSON documents in a native binary format, with functions to extract and update values. I use JSON for flexible attributes that do not need the same constraints and joins as core relational data, but keep frequently filtered, joined, and validated fields relational when practical. A generated column can expose a JSON path as a typed/indexable column for a measured query pattern.

## Key Points

- MySQL 5.7.8+ supports a native JSON type; invalid JSON text is rejected when inserted into a JSON column. A JSON column cannot be indexed directly as an arbitrary document.
- `JSON_EXTRACT(doc, '$.path')` returns a JSON value; `->` is shorthand. `->>` extracts and unquotes a scalar as text (MySQL 5.7.13+).
- JSON path and scalar types matter. Cast extracted values when numeric comparison is needed; lexical string ordering is not numeric ordering.
- `JSON_SET` can add or replace a path; `JSON_REMOVE` removes a path. Test missing keys and SQL NULL/JSON null behavior explicitly.
- A generated column can derive a typed scalar from JSON and be indexed. Define its type, collation, and null behavior; the index is on the generated column/expression, not a general index over every document key.
- `JSON_TABLE` converts JSON data into rows and is available from MySQL 8.0.4. Use it for appropriate tabular expansion, but avoid placing normalized relational collections into JSON without a reason.
- JSON can create schema drift, larger payloads, and weaker foreign-key/constraint enforcement compared with relational columns.

## Minimal Example

```sql
SELECT order_id,
       JSON_UNQUOTE(JSON_EXTRACT(attributes, '$.color')) AS color
FROM product_variants
WHERE JSON_UNQUOTE(JSON_EXTRACT(attributes, '$.color')) = 'blue';
```

For frequent filtering, define a generated column such as `color VARCHAR(30) GENERATED ALWAYS AS (...)` and index it. Check exact expression/type support and verify the query plan.

## Common Traps

- Extracted JSON numbers may need an explicit cast before numeric comparison; do not rely on text ordering.
- A missing path and JSON null are not necessarily the same as SQL NULL. Test the desired condition explicitly.
- JSON is not automatically more flexible or faster; frequently queried fields may belong in ordinary columns.
- Generated/indexed expressions add storage and write cost and must match the query expression and type.

## Likely Follow-Ups

**When use JSON instead of columns?** For optional or evolving attributes with limited relational constraints; use normal columns for stable, frequently filtered/joined business fields.

**How index a JSON field?** Extract it with a generated column of a suitable type, add an index, then check EXPLAIN for the actual query.

**What does JSON_TABLE do?** It maps JSON values into a relational row/column form, useful for querying arrays/documents as rows when supported.

## MySQL References

Examples target MySQL 8.4. JSON support began in MySQL 5.7; `->>` is available from 5.7.13 and JSON_TABLE from 8.0.4. See [JSON functions](https://dev.mysql.com/doc/refman/8.4/en/json-functions.html), [JSON data type](https://dev.mysql.com/doc/refman/8.4/en/json.html), and [generated columns](https://dev.mysql.com/doc/refman/8.4/en/create-table-generated-columns.html).
