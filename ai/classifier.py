from sentence_transformers import SentenceTransformer, util
import torch
from inventory.models import Inventory

# Load model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def encode_inventory_text(inv):
    """
    Combine inventory and medicine fields into a single string for embedding.
    """
    classifications = " ".join([c.label for c in inv.medicine.classification.all()])
    return (
        
        f"{inv.medicine.generic_name} "
        f"{inv.medicine.brand_name}"
        f"{classifications}"
    )


def build_inventory_index():
    """
    Build vector embeddings for all inventory rows.
    Returns:
        - inventory_list: list of Inventory objects
        - embedding_matrix: stacked tensor of embeddings
    """
    inventory_list = list(Inventory.objects.select_related("medicine"))
    texts = [encode_inventory_text(inv) for inv in inventory_list]

    # Batch encode all inventory texts
    embedding_matrix = model.encode(texts, convert_to_tensor=True)

    return inventory_list, embedding_matrix


# Precompute at startup
inventory_list, embedding_matrix = build_inventory_index()


def ai_inventory_search(query, top_k=10):
    """
    Search inventory using AI embeddings.
    Returns top_k results with cosine similarity scores.
    """
    if not inventory_list:
        return []

    # Encode user query
    query_vector = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity in batch
    scores = util.cos_sim(query_vector, embedding_matrix)[0]  # shape: (num_inventory,)

    # Get top K indices
    top_results = torch.topk(scores, k=min(top_k, len(scores)))

    results = []
    for score, idx in zip(top_results.values.tolist(), top_results.indices.tolist()):
        results.append((score, inventory_list[idx]))

    return results
