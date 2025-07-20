import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import torch

model = SentenceTransformer("all-mpnet-base-v2")

df = pd.read_csv("datasets/resources_with_embeddings.csv")

def parse_embedding(embedding_str):
    return np.array(list(map(float, embedding_str.split(","))), dtype=np.float32)

tqdm.pandas(desc="Parsing embeddings")
df["embedding_title"] = df["embedding_title"].progress_apply(parse_embedding)
df["embedding_description"] = df["embedding_description"].progress_apply(parse_embedding)

df["combined_embedding"] = df.apply(lambda row: (row["embedding_title"] + row["embedding_description"]) / 2, axis=1)

query = "Convolutional Neural Networks for image classification"
query_embedding = model.encode(query, convert_to_tensor=True)

combined_embeddings = np.stack(df["combined_embedding"].values)
combined_embeddings_tensor = torch.from_numpy(combined_embeddings)

cos_scores = util.cos_sim(query_embedding, combined_embeddings_tensor)[0].cpu().numpy()

df["similarity"] = cos_scores
df_sorted = df.sort_values(by="similarity", ascending=False).head(20)

for idx, row in df_sorted.iterrows():
    print(f"{row['title']} ({row['url']}) - Similarity: {row['similarity']:.4f}")

df_sorted.to_csv("datasets/semantic_ranked_results.csv", index=False)
print("\n Ranking complete. Saved as datasets/semantic_ranked_results.csv")
