# MySQL Interview Revision Syllabus

Audience: full-stack developer with 2 years of overall development experience and working MySQL knowledge targeting interviews in India. Not 2 years of database-specialist experience. Assume CRUD, simple joins, and application database usage; revise interview gaps rather than teach from scratch. Baseline: MySQL 8.4 LTS and InnoDB; explain relevant 8.0 and legacy 5.7 differences explicitly.

Status: all 24 topic pairs created on 2026-11-08 following approval; database execution requires authorized practice-instance access. [start.md](start.md) owns topic filenames, links, and revision status.

## Interview Priorities

Planning basis reviewed on 2026-11-08: India-facing interview preparation material plus public SQL assessment guidance. These sources support topic selection, not measured interview frequency or guarantees about any company's questions.

- **Core:** common SQL questions and query patterns, keys, basic indexes, normalization, and transactions. These appear first in the recommended order.
- **Useful:** window functions, CTEs, basic EXPLAIN, application integration, isolation, and everyday concurrency reasoning.
- **Optional:** storage internals, replication/recovery, and scaling specifics. Keep these at recognition/trade-off level unless a job description requires more.
- The order approximates common preparation priorities, not a verified "most asked" ranking across India. Keep questions, query exercises, complete answers, and scenario-based practice; reduce specialist depth, not correctness.
- No phases or prerequisite-heavy foundation block. Explain a needed SQL concept briefly inside an early interview-pattern answer and link to its registered topic for further revision.
- Deep DBA administration, vendor certifications, and warehouse-specific SQL are outside the default scope. Optional stretch material is not required for core revision.

## Topics In Interview-Priority Order

Read top to bottom. Stable IDs and slugs are retained so future filenames do not change when priorities change; IDs do not determine study order.

| ID | Topic | Coverage | Priority |
|---|---|---|---|
| 06 | Joins and missing-data queries | INNER/LEFT/RIGHT/self/CROSS joins, ON vs WHERE, unmatched customers, duplicate rows from joins, FULL OUTER JOIN emulation | Core |
| 05 | Aggregation and conditional reporting | COUNT variants, SUM/AVG, GROUP BY vs HAVING, ONLY_FULL_GROUP_BY, totals per customer/department, simple conditional aggregation, avoiding double counting | Core |
| 07 | Subqueries and existence checks | Scalar/derived/correlated subqueries, EXISTS/NOT EXISTS, IN/NOT IN NULL traps, subquery vs join without universal performance claims | Core |
| 10 | Interview query patterns | Second/Nth distinct salary, duplicate detection/removal, latest order, top N per group, above-average salary; optional stretch: consecutive activity and month-on-month reporting | Core |
| 03 | Keys, constraints, and schema changes | Primary/foreign/unique/composite keys, NULL in UNIQUE, CHECK/defaults, AUTO_INCREMENT, basic ALTER, DELETE vs TRUNCATE vs DROP and rollback limits | Core |
| 13 | Index design | What an index does, read vs write costs, primary vs secondary, composite/leftmost-prefix basics, why an index may not be used, covering indexes; advanced index types optional | Core |
| 11 | Schema design and normalization | One-to-many/many-to-many, junction tables, 1NF/2NF/3NF, anomalies, sensible denormalization, users/orders/products schema; BCNF as a short follow-up | Core |
| 15 | Transactions and ACID | ACID in a payment/order example, START TRANSACTION/COMMIT/ROLLBACK, autocommit/savepoints, keeping writes atomic, DDL implicit commits vs atomic DDL | Core |
| 02 | Data types, NULL, and expressions | DECIMAL vs FLOAT for money, INT/BIGINT, CHAR/VARCHAR, DATETIME/TIMESTAMP, BOOLEAN, NULL comparisons, COALESCE/CASE, casts and strict modes | Core |
| 01 | SQL foundations and execution order | SQL vs MySQL, DDL/DML/DCL/TCL, logical SELECT order, WHERE/HAVING, DISTINCT, ORDER BY/LIMIT; quick interview recap, not a beginner introduction | Core |
| 04 | Filtering, functions, and dates | LIKE wildcards, strings/numbers, date arithmetic and month filtering, half-open ranges, UTC vs IST, basic collation; REGEXP as a follow-up | Core |
| 08 | CTEs and set operations | WITH for readable queries, UNION vs UNION ALL, compatible result columns; recursive CTEs and INTERSECT/EXCEPT version support as optional follow-ups | Useful |
| 09 | Window functions | ROW_NUMBER vs RANK vs DENSE_RANK, PARTITION BY, top N per group, running totals, LAG/LEAD, filtering through CTEs; detailed frames/FIRST_VALUE/LAST_VALUE optional | Useful |
| 14 | EXPLAIN and query optimization | Read basic EXPLAIN, selected index/rows/access type, avoid SELECT *, sargable filters, diagnose a slow query, EXPLAIN ANALYZE executes the query; detailed statistics/Performance Schema optional | Useful |
| 21 | Application integration and security | Prepared statements/SQL injection, least privilege, connection pooling, same connection for a transaction, ORM N+1, basic upserts and duplicate-request handling | Useful |
| 18 | Pagination and large-table changes | LIMIT/OFFSET, deterministic ordering, keyset pagination for growing lists, small batches for updates/deletes; archival/online DDL risks optional | Useful |
| 16 | Isolation levels and MVCC | Dirty/non-repeatable/phantom reads, InnoDB default REPEATABLE READ, READ COMMITTED, basic snapshots vs locking reads and lost updates; write skew optional | Useful |
| 17 | Locks, deadlocks, and safe writes | Two-session inventory example, FOR UPDATE, atomic conditional UPDATE, optimistic version checks, deadlocks and bounded retries; gap/next-key/metadata locks and NOWAIT/SKIP LOCKED optional | Useful |
| 19 | Views and stored objects | View vs table, procedures vs functions, basic parameters/triggers and trade-offs, no native materialized views; detailed updatability/events/cursors optional | Useful |
| 20 | JSON and generated columns | Simple JSON extraction, relational columns vs JSON, generated-column purpose; JSON_TABLE, JSON indexing and full-text search optional | Useful |
| 12 | InnoDB architecture and storage | InnoDB vs MyISAM, clustered primary/secondary indexes, buffer-pool purpose; pages and redo/undo/binlog only as brief recognition-level follow-ups | Optional |
| 22 | Replication and recovery | Source/replica, replication lag and stale reads, backup vs replica, restore testing; GTID, failover and point-in-time recovery only at overview level | Optional |
| 23 | Partitioning and scaling decisions | Partitioning vs sharding vs indexing, read replicas, caching/invalidation, OLTP vs OLAP and SQL vs NoSQL trade-offs; partition types/pruning/key restrictions optional detail | Optional |
| 24 | Mixed interview scenarios and mock round | Medium multi-table queries, choose a basic index, defend a small schema, safe order/payment writes, explain a slow endpoint; no DBA incident deep dive required | Core |

## Content And Practice Contract

- Each row above is one topic pair in `notes/`: `NN-topic-slug.md` and `NN-topic-slug-exercises.md`. Subtopics belong inside their parent module; any new standalone topic must get its own registered pair.
- Notes: short, directly speakable 2-4 sentence answers, compact key points, a minimal example/result, traps, and answered follow-ups. Aim for 300-600 words excluding SQL/output.
- Exercises: 10-15 questions per topic, default 12, all with complete answers. Query topics use 7 scenario query tasks + 3 debugging/edge-case tasks + 2 interview questions. Other topics use 6 production scenarios + 4 SQL/DDL/diagnostic/timeline tasks + 2 interview questions.
- Include runnable schema/sample data where relevant, explicit business assumptions, executable MySQL solutions, expected results/effects, and short explanations. Use original scenarios, not copied question-bank answers.
- Keep difficulty mainly quick-to-medium for a 2-year full-stack developer, with at most 2 clearly labelled optional stretch questions per file. Optional topics still get the same fully answered exercise format when requested; their depth is introductory, not DBA-level.
- Navigation: `start.md` links to both files; both files link back to `start.md` and to each other. Pending files remain unlinked until created.

## Revision Loop

Quick diagnostic -> skim concise answers -> attempt exercises before reading answers -> run/check queries -> explain the approach and one trap aloud. Revisit only gaps; do not mark revision complete merely because files exist.

Spend roughly 30-60 minutes on a familiar topic and 60-90 minutes on a gap, then reattempt missed questions. Follow the displayed interview-priority order; skip optional specialist topics until required. These are flexible revision estimates, not deadlines; solving every exercise can take longer.

## Sources And Limits

- [InterviewBit SQL interview questions](https://www.interviewbit.com/sql-interview-questions/), page dated 2026-03-24, accessed 2026-11-08: India-facing preparation covering joins, subqueries, constraints, indexes, normalization, and stored objects. Mixed-dialect examples must not be used as MySQL correctness references.
- [HackerRank SQL Advanced assessment](https://www.hackerrank.com/skills-verification/sql_advanced), accessed 2026-11-08: public assessment guidance explicitly includes SQL pivots. Global assessment context, not India-specific interview-frequency data.
- [MySQL 8.4 reference manual](https://dev.mysql.com/doc/refman/8.4/en/), accessed 2026-11-08: correctness baseline for MySQL syntax, InnoDB, optimization, stored objects, replication, and partitioning; not an interview-trend source.

The displayed ordering and depth are curriculum judgments for a 2-year full-stack developer, not a database specialist. No representative India-wide 2026 interview-frequency dataset has been verified here.
