from db.mongo_client import atlas_client, COLLECTION_NAME
import logging

logger = logging.getLogger(__name__)

def save_incident(analysis):
    try:
        collection = atlas_client.get_collection(COLLECTION_NAME)
        collection.update_one(
            {"incident_id": analysis.incident_id},
            {"$set": analysis.dict()},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Failed to save incident: {e}")

def get_incidents(limit=50):
    try:
        collection = atlas_client.get_collection(COLLECTION_NAME)
        items = list(collection.find().sort("timestamp", -1).limit(limit))
        for i in items:
            i["_id"] = str(i["_id"])
        return items
    except Exception as e:
        logger.error(f"Failed to fetch incidents: {e}")
        return []
