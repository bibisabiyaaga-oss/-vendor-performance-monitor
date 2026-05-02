import chromadb
from chromadb.utils import embedding_functions

print("Connecting to ChromaDB...")
client = chromadb.Client()

ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="vendor_knowledge",
    embedding_function=ef
)

documents = [
    "A vendor performance score above 90 indicates exceptional performance and reliability.",
    "Delivery rate below 80% is considered poor and requires immediate intervention.",
    "Quality rating of 4.5 or above out of 5 indicates excellent product quality.",
    "Vendors with contract values above $100,000 should receive quarterly performance reviews.",
    "A performance score between 70-89 indicates good performance with room for improvement.",
    "Vendors with delivery rates above 95% are considered highly reliable partners.",
    "Quality ratings below 3.0 indicate serious quality issues requiring escalation.",
    "Contract renewal decisions should consider minimum 12 months of performance data.",
    "Vendors scoring below 60 in performance should be placed on improvement plans.",
    "Top performing vendors with scores above 95 should be considered for preferred partner status."
]

ids = [f"doc_{i}" for i in range(len(documents))]

collection.add(documents=documents, ids=ids)

print(f"Successfully seeded {len(documents)} documents to ChromaDB!")
print("ChromaDB is ready for use!")