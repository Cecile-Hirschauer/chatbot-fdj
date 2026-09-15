import sqlite3
from pathlib import Path

import pandas as pd


def setup_database() -> None:
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data"
    csv_path = data_dir / "lottery_draws.csv"
    db_path = data_dir / "lottery.db"

    # Read the CSV file (FDJ files often use ';' as a separator)
    # Adjust 'sep' if it uses standard commas
    df = pd.read_csv(csv_path, sep=";")

    # Connect to SQLite and write the dataframe to a table named 'draws'
    with sqlite3.connect(db_path) as conn:
        df.to_sql("draws", conn, if_exists="replace", index=False)

    print(f"Successfully created database at {db_path}")
    print("Table 'draws' contains the following columns:")
    for col in df.columns:
        print(f"- {col}")


if __name__ == "__main__":
    setup_database()
