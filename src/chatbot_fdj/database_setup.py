import sqlite3
from pathlib import Path

import pandas as pd


def setup_database() -> None:
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data"
    csv_path = data_dir / "lottery_draws.csv"
    db_path = data_dir / "lottery.db"

    df = pd.read_csv(csv_path, sep=";")

    # Mapping dictionary to translate and filter the domain data
    columns_mapping = {
        "annee_numero_de_tirage": "draw_year_id",
        "jour_de_tirage": "draw_day",
        "date_de_tirage": "draw_date",
        "boule_1": "ball_1",
        "boule_2": "ball_2",
        "boule_3": "ball_3",
        "boule_4": "ball_4",
        "boule_5": "ball_5",
        "numero_chance": "lucky_number"
    }

    # Filter and rename columns
    clean_df = df[list(columns_mapping.keys())].rename(columns=columns_mapping)

    # Convert dates to a standard SQL format (YYYY-MM-DD) for easier queries
    clean_df["draw_date"] = pd.to_datetime(clean_df["draw_date"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")

    with sqlite3.connect(db_path) as conn:
        clean_df.to_sql("draws", conn, if_exists="replace", index=False)

    print(f"Successfully created clean database at {db_path}")
    print("Table 'draws' contains the following finalized columns:")
    for col in clean_df.columns:
        print(f"- {col}")

if __name__ == "__main__":
    setup_database()
