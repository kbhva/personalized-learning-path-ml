import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import numpy as np
import os

df = pd.read_csv("datasets/resources.csv")

model = SentenceTransformer("all-mpnet-base-v2")

def embed_to_str(embedding):
    return ",".join([str(x) for x in embedding])


title_embeddings = []
desc_embeddings = []

print(" Generating semantic embeddings for all videos...")

for idx, row in tqdm(df.iterrows(), total=len(df)):
    title = str(row["title"])
 
    description = str(row["title"])  

    title_emb = model.encode(title, show_progress_bar=False)
    desc_emb = model.encode(description, show_progress_bar=False)

    title_embeddings.append(embed_to_str(title_emb))
    desc_embeddings.append(embed_to_str(desc_emb))

df["embedding_title"] = title_embeddings
df["embedding_description"] = desc_embeddings


os.makedirs("datasets", exist_ok=True)
df.to_csv("datasets/resources_with_embeddings.csv", index=False)

print(" Semantic enrichment complete. Saved as datasets/resources_with_embeddings.csv")
