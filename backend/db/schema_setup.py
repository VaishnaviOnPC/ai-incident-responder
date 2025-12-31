# schema_setup.py
from db.mongo_client import atlas_client, COLLECTION_NAME

def create_indexes():
    collection = atlas_client.get_collection(COLLECTION_NAME)

    print(f"[+] Creating indexes on `{COLLECTION_NAME}`...")

    # Ensure incident_id is unique
    collection.create_index(
        [("incident_id", 1)],
        unique=True,
        name="incident_id_unique"
    )

    # Text search on AI-generated insights
    collection.create_index(
        [
            ("summary", "text"),
            ("root_cause", "text"),
            ("recommended_actions", "text")
        ],
        name="incident_text_search"
    )

    # Filter by service
    collection.create_index(
        [("service_name", 1)],
        name="service_index"
    )

    # Filter by severity
    collection.create_index(
        [("severity", 1)],
        name="severity_index"
    )

    # Sort by time (most recent first)
    collection.create_index(
        [("timestamp", -1)],
        name="timestamp_desc_index"
    )

    print("[✓] Indexes created successfully.")


if __name__ == "__main__":
    create_indexes()
