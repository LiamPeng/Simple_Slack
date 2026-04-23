# CS6083 Project 1 — **snickr** database design

Database design and SQL artifacts for **snickr**, a Slack-like collaboration app.

## Project structure

```text
Simple_Slack/
├── README.md
├── diagrams/
│   ├── ER_Diagram.mmd
│   ├── ER_Diagram.png
│   └── ER_Diagram.svg
├── report/
│   └── reports.md
├── sql/
│   ├── project1_table.sql
│   ├── project1_data.sql
│   └── project1_queries.sql
└── output/
    └── output.md
```

## Environment

- **Database:** PostgreSQL
- **Client:** `psql` (tested locally)

## How to run

From the project root, create a database and run the SQL files in order: schema, sample data, then queries.

```bash
createdb project1_db
psql -d project1_db -f sql/project1_table.sql
psql -d project1_db -f sql/project1_data.sql
psql -d project1_db -f sql/project1_queries.sql > output/output.md
```

## Contents

- **diagrams/** — ER source (Mermaid) and exports (SVG/PNG)
- **report/** — project write-up
- **sql/** — table definitions, sample data, and query scripts
- **output/** — saved query output (e.g. from the command above)

## Notes

The work is split into four parts:

1. Schema design
2. Sample data
3. SQL queries
4. Report and diagrams
