import snowflake.connector
import os
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

FILE_TO_TABLE = {
    "sale": "RAW_LISTINGS_FOR_SALE",
    "rent": "RAW_LISTINGS_FOR_RENT",
}


def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def setup(conn):
    """Create stage and raw tables if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE OR REPLACE STAGE internal_zillow_stage")
        for table in FILE_TO_TABLE.values():
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    filename    VARCHAR,
                    raw_data    VARIANT,
                    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """)
    logger.info("Stage and tables ready.")


def resolve_table(file_path):
    """Map a file path to its target Snowflake table based on filename prefix."""
    file_name = os.path.basename(file_path).lower()
    for prefix, table in FILE_TO_TABLE.items():
        if file_name.startswith(prefix):
            return table
    raise ValueError(
        f"Cannot resolve target table for '{file_name}'. "
        f"Expected filename to start with one of: {list(FILE_TO_TABLE.keys())}"
    )


def load_file(conn, file_path):
    """Stage and COPY a single JSON file into the appropriate raw table."""
    file_path = file_path.strip()
    file_name = os.path.basename(file_path)
    target_table = resolve_table(file_path)

    with conn.cursor() as cur:
        cur.execute(f"PUT 'file://{os.path.abspath(file_path)}' @internal_zillow_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        logger.info("Staged: %s", file_name)

        cur.execute(f"""
            COPY INTO {target_table} (filename, raw_data)
            FROM (
                SELECT '{file_name}', $1
                FROM @internal_zillow_stage/{file_name}
            )
            FILE_FORMAT = (TYPE = JSON)
            ON_ERROR = ABORT_STATEMENT
        """)

        row = cur.fetchone()
        rows_loaded = int(row[3]) if row else 0
        logger.info("Loaded %d rows into %s from %s", rows_loaded, target_table, file_name)


if __name__ == "__main__":
    files = sys.argv[1:] or [
        "sale_data.json",
        "rent_data.json",
    ]

    conn = get_connection()
    setup(conn)

    failed = []
    for file_path in files:
        try:
            load_file(conn, file_path)
        except Exception as e:
            logger.error("Failed to load %s: %s", file_path, e)
            failed.append(file_path)

    conn.close()

    if failed:
        logger.error("The following files failed: %s", failed)
        sys.exit(1)

    logger.info("All files loaded successfully.")
