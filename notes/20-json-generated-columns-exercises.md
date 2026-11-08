# JSON And Generated Columns: Exercises

[Notes](20-json-generated-columns.md) | [Topic index](../start.md)

12 questions: 7 query tasks, 3 edge/debugging tasks, and 2 interview questions. Use MySQL 8.4; JSON type support is available from 5.7.8, JSON_TABLE from 8.0.4. The fixture includes a missing JSON path and a SQL NULL document.

## Setup

```sql
CREATE TABLE json_products (
 product_id INT PRIMARY KEY,
 attributes JSON NULL,
 color VARCHAR(30) GENERATED ALWAYS AS
   (JSON_UNQUOTE(JSON_EXTRACT(attributes,'$.color'))) VIRTUAL,
 INDEX ix_json_products_color(color)
) ENGINE=InnoDB;
INSERT INTO json_products(product_id,attributes) VALUES
 (1,'{"color":"blue","weight":2.5}'),
 (2,'{"color":"red","weight":1.0}'),
 (3,'{"weight":3.0}'),
 (4,NULL);
```

## 1. Extract A Color

Return each product ID and its color, showing SQL NULL when the path is missing.

**Expected result:** Product 1 blue, product 2 red, products 3 and 4 NULL.

<details><summary>Show answer</summary>

```sql
SELECT product_id,JSON_UNQUOTE(JSON_EXTRACT(attributes,'$.color')) AS color
FROM json_products ORDER BY product_id;
```
The missing path and SQL NULL document produce NULL for this extraction.
</details>

## 2. Filter A JSON Scalar

Return products whose JSON color is blue.

**Expected result:** Product 1.

<details><summary>Show answer</summary>

```sql
SELECT product_id FROM json_products
WHERE JSON_UNQUOTE(JSON_EXTRACT(attributes,'$.color'))='blue' ORDER BY product_id;
```
The extraction is unquoted text for comparison.
</details>

## 3. Use The Generated Column

Return products with color red using the generated field.

**Expected result:** Product 2.

<details><summary>Show answer</summary>

```sql
SELECT product_id FROM json_products WHERE color='red' ORDER BY product_id;
```
The virtual generated column can be indexed in InnoDB; verify the optimizer uses it for the workload.
</details>

## 4. Extract And Compare A Numeric Attribute

Return products with weight greater than 2.0 using a numeric cast.

**Expected result:** Products 1 and 3.

<details><summary>Show answer</summary>

```sql
SELECT product_id FROM json_products
WHERE CAST(JSON_UNQUOTE(JSON_EXTRACT(attributes,'$.weight')) AS DECIMAL(6,2))>2.0
ORDER BY product_id;
```
Cast to a numeric type so comparison is numeric rather than lexical.
</details>

## 5. Add A JSON Path

For product 3, set its color to green.

**Expected result:** Product 3's document contains color green while preserving weight.

<details><summary>Show answer</summary>

```sql
UPDATE json_products
SET attributes=JSON_SET(attributes,'$.color','green')
WHERE product_id=3;
```
This is a modifying statement; use only the isolated fixture. JSON_SET adds the missing path.
</details>

## 6. Remove A JSON Path

Return a SELECT expression that removes color from product 1 without changing the table.

**Expected result:** A projected JSON document without the color key; stored data remains unchanged.

<details><summary>Show answer</summary>

```sql
SELECT JSON_REMOVE(attributes,'$.color') AS without_color
FROM json_products WHERE product_id=1;
```
JSON_REMOVE returns a transformed value; SELECT alone does not persist it.
</details>

## 7. Expand An Array With JSON_TABLE

Given a JSON document `'{"tags":["new","sale"]}'`, return one row per tag.

**Expected result:** Two rows, new and sale.

<details><summary>Show answer</summary>

```sql
SELECT tag FROM JSON_TABLE(
 '{"tags":["new","sale"]}', '$.tags[*]' COLUMNS(tag VARCHAR(30) PATH '$')
) AS jt ORDER BY tag;
```
JSON_TABLE requires MySQL 8.0.4+.
</details>

## 8. Debug String Ordering Of JSON Numbers

Why can comparing extracted numeric text to `'10'` produce surprising ordering relative to `'2'`? Correct the comparison.

**Expected result:** Cast the extracted value to DECIMAL before numeric comparison.

<details><summary>Show answer</summary>

```sql
WHERE CAST(JSON_UNQUOTE(JSON_EXTRACT(attributes,'$.weight')) AS DECIMAL(8,2))>2
```
String comparison is lexical; numeric meaning needs a numeric type.
</details>

## 9. Distinguish Missing Path From SQL NULL

How can a query identify documents where the color path is absent, while excluding SQL NULL documents?

**Expected result:** Check the extracted path IS NULL and the document IS NOT NULL.

<details><summary>Show answer</summary>

```sql
SELECT product_id FROM json_products
WHERE attributes IS NOT NULL
  AND JSON_EXTRACT(attributes,'$.color') IS NULL
ORDER BY product_id;
```
Product 3 is returned. Confirm exact null/missing semantics for the JSON expression used.
</details>

## 10. Review JSON Versus Relational Columns

A field is required in every query filter and joined to another table. Should it stay only in JSON?

**Expected result:** Usually model it relationally for constraints, joins, and indexing.

<details><summary>Show answer</summary>

Usually use a normal typed column for stable, required, frequently queried relationships. A generated indexed column can be a transitional option, but JSON does not provide the same foreign-key and column-level constraint model.
</details>

## 11. Interview: JSON Trade-Off

Give one suitable JSON use and one reason not to store everything as JSON.

**Expected result:** Flexible attributes versus weaker relational constraints/query clarity.

<details><summary>Show answer</summary>

JSON suits optional or evolving attributes whose structure varies. Stable fields used for joins, constraints, or frequent filters are often clearer and safer as relational columns.
</details>

## 12. Interview: Generated Column Index

How can a generated column help query a JSON property?

**Expected result:** Extract/cast a scalar into a generated typed column, index it, and verify the plan.

<details><summary>Show answer</summary>

Define a generated column using the JSON path expression and an appropriate SQL type, then index that generated column. This supports a known scalar access pattern but adds index/write cost; verify EXPLAIN and semantics for missing values.
</details>
