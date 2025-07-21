import pandas as pd
from pathlib import Path


folder_path = Path("datasets/scraped_csvs")


csv_files = list(folder_path.glob("*.csv"))


dfs = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(dfs, ignore_index=True)

combined_df = combined_df.drop_duplicates(subset="url")


combined_df = combined_df.sample(frac=1).reset_index(drop=True)

combined_df.to_csv("datasets/resources.csv", index=False)

print(" All CSVs merged cleanly into datasets/resources.csv")
print(f" Total videos in dataset: {len(combined_df)}")
