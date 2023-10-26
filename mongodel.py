from pymongo import MongoClient

# Connect to MongoDB (adjust the connection string as needed)
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']  # Replace 'your_database_name' with your actual database name
collection = db['your_collection_name']  # Replace 'your_collection_name' with your actual collection name

# Delete all documents in the collection
result = collection.delete_many({})

# Print the result (number of documents deleted)
print(f"Deleted {result.deleted_count} documents")
