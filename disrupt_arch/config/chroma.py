from chromadb import HttpClient

chroma_client = HttpClient(host="localhost", port=8000)
chroma_client.heartbeat()
