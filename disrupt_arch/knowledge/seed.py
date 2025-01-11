import logging

from chromadb import HttpClient
from chromadb.utils import embedding_functions

chroma_client = HttpClient(host="localhost", port=8000)

default_ef = embedding_functions.DefaultEmbeddingFunction()

rules = [
    {
        "description": "If risk level is None request risk assessment",
        "metadata": {"action": "assess_risk", "target": "RiskAssessmentAgent"},
    },
    {
        "description": "If overdue days > 120 and risk level is High, escalate case.",
        "metadata": {"action": "escalate_case", "target": "LegalAgent"},
    },
    {
        "description": "If risk level is Moderate and overdue days are between 60 and 120, escalate case.",
        "metadata": {"action": "escalate_case", "target": "LegalAgent"},
    },
    {
        "description": "If risk level is Low, contact the debtor directly with a payment plan.",
        "metadata": {"action": "contact_debtor", "target": "CommunicationAgent"},
    },
]


def seed_busines_ules():
    global rules

    collection = chroma_client.get_or_create_collection(
        name="business_rules", embedding_function=default_ef
    )

    for index, rule in enumerate(rules, start=1):
        collection.add(
            documents=[rule["description"]],
            metadatas=[rule["metadata"]],
            ids=[str(index)],
        )

    rules = collection.get()

    logging.info(f"Seeded business rules:\n{rules}")


def seed_knowledge_base():
    """Seed the knowledge base with initial information."""
    try:
        seed_busines_ules()
    except Exception as e:
        logging.error(f"Error seeding knowledge base: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_knowledge_base()
