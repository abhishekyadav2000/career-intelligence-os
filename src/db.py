"""SQLite database for SQL analytics demo."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "career_intel.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Return SQLite connection with row factory."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(companies_df, jobs_df, contacts_df, db_path: Path | None = None) -> None:
    """Initialize SQLite tables from DataFrames."""
    path = db_path or DB_PATH
    conn = get_connection(path)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS contacts;
        DROP TABLE IF EXISTS jobs;
        DROP TABLE IF EXISTS companies;

        CREATE TABLE companies (
            company_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            location TEXT,
            industry TEXT,
            priority_tier TEXT,
            h1b_confidence INTEGER,
            dfw_fit INTEGER,
            role_fit INTEGER
        );

        CREATE TABLE jobs (
            job_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            company_name TEXT,
            title TEXT,
            location TEXT,
            role_cluster TEXT,
            priority_tier TEXT,
            business_problem TEXT,
            status TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE contacts (
            contact_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            company_name TEXT,
            contact_type TEXT,
            persona TEXT,
            status TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
    """)

    for _, row in companies_df.iterrows():
        cur.execute(
            """INSERT INTO companies VALUES (?,?,?,?,?,?,?,?)""",
            (
                row["company_id"], row["company_name"], row.get("location"),
                row.get("industry"), row.get("priority_tier"),
                int(row.get("h1b_confidence", 0) or 0),
                int(row.get("dfw_fit", 0) or 0),
                int(row.get("role_fit", 0) or 0),
            ),
        )

    for _, row in jobs_df.iterrows():
        cur.execute(
            """INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                row["job_id"], row["company_id"], row["company_name"],
                row.get("title"), row.get("location"), row.get("role_cluster"),
                row.get("priority_tier"), row.get("business_problem"), row.get("status"),
            ),
        )

    for _, row in contacts_df.iterrows():
        cur.execute(
            """INSERT INTO contacts VALUES (?,?,?,?,?,?)""",
            (
                row["contact_id"], row["company_id"], row["company_name"],
                row.get("contact_type"), row.get("persona"), row.get("status"),
            ),
        )

    conn.commit()
    conn.close()


# Demo SQL queries showcasing analytics capability
DEMO_QUERIES: dict[str, str] = {
    "jobs_by_tier": """
        SELECT priority_tier, COUNT(*) AS job_count
        FROM jobs
        GROUP BY priority_tier
        ORDER BY job_count DESC;
    """,
    "top_companies_by_jobs": """
        SELECT c.company_name, c.industry, COUNT(j.job_id) AS open_roles
        FROM companies c
        JOIN jobs j ON c.company_id = j.company_id
        WHERE j.status = 'open'
        GROUP BY c.company_name, c.industry
        ORDER BY open_roles DESC
        LIMIT 10;
    """,
    "contacts_by_type": """
        SELECT contact_type, COUNT(*) AS contact_count,
               SUM(CASE WHEN status = 'not_contacted' THEN 1 ELSE 0 END) AS pending
        FROM contacts
        GROUP BY contact_type;
    """,
    "tier1_pipeline": """
        SELECT c.company_name, c.h1b_confidence, COUNT(j.job_id) AS jobs,
               COUNT(ct.contact_id) AS contacts
        FROM companies c
        LEFT JOIN jobs j ON c.company_id = j.company_id
        LEFT JOIN contacts ct ON c.company_id = ct.company_id
        WHERE c.priority_tier LIKE 'Tier 1%'
        GROUP BY c.company_name, c.h1b_confidence
        ORDER BY jobs DESC
        LIMIT 15;
    """,
    "industry_breakdown": """
        SELECT industry, COUNT(DISTINCT company_id) AS companies,
               AVG(h1b_confidence) AS avg_h1b_confidence
        FROM companies
        GROUP BY industry
        ORDER BY companies DESC;
    """,
}


def run_query(sql: str, db_path: Path | None = None) -> list[dict]:
    """Execute a SQL query and return results as list of dicts."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description] if cur.description else []
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.close()
    return rows
