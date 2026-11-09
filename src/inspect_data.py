import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = {
    "Orders": "olist_orders_dataset.csv",
    "Order Items": "olist_order_items_dataset.csv",
    "Sellers": "olist_sellers_dataset.csv",
    "Reviews": "olist_order_reviews_dataset.csv"
}

for name, filename in files.items():
    df = pd.read_csv(DATA_DIR / filename)

    print("\n" + "=" * 50)
    print(f"{name} DATASET")
    print("=" * 50)

    print("Rows and columns:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))

    print("\nMissing values:")
    print(df.isnull().sum())