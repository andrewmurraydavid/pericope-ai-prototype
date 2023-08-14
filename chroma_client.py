import uuid
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os
import dotenv

dotenv.load_dotenv()

CHROMA_HOST = os.environ.get('CHROMA_HOST', 'localhost')
CHROMA_PORT = int(os.environ.get('CHROMA_PORT', '8000'))
CHROMA_SSL = int(os.environ.get('CHROMA_SSL', '0')) == 1
MODEL_NAME = os.environ.get('MODEL_NAME', 'all-distilroberta-v1')
COLLECTION = os.environ.get('COLLECTION_NAME', 'test-collection')

print("ChromaDB client configuration:", CHROMA_HOST, CHROMA_PORT, CHROMA_SSL, MODEL_NAME, COLLECTION)


class ChromaClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaClient, cls).__new__(cls)
            cls._instance.init_chroma()
        return cls._instance

    def init_chroma(self):
        print("Initializing ChromaDB client...")
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=443, ssl=True)
        sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
            model_name=MODEL_NAME
        )
        self.collection = self.client.get_collection(COLLECTION, embedding_function=sentence_transformer_ef)

    def query(self, story_name, desired_results=10, max_attempts=10):
        n = desired_results
        attempt = 0
        final_results = []

        while len(final_results) < desired_results and attempt < max_attempts:
            # Fetch results
            results = self.collection.query(
                query_texts=story_name,
                n_results=n,
                include=["metadatas", "distances"]
            )

            matched_pericopes = results
            pericope_dict = {}

            for id_list, dist_list, meta_list in zip(matched_pericopes['ids'], matched_pericopes['distances'], matched_pericopes['metadatas']):
                for id_val, dist, meta in zip(id_list, dist_list, meta_list):
                    pericope_id = meta['pid']

                    # If pericope doesn't exist or has larger distance, update/insert the record
                    if pericope_id not in pericope_dict or pericope_dict[pericope_id]['distance'] > dist:
                        pericope_dict[pericope_id] = {
                            'uuid': id_val,
                            'id': pericope_id,
                            'pericope': meta['pericope'],
                            'distance': dist,
                            'metadata': {
                                "pericope": meta['pericope'],
                                "reference": meta['reference'],
                                "start": meta['start'],
                                "end": meta['end']
                            }
                        }

            # Append non-duplicate results to final results
            for item in pericope_dict.values():
                if item['id'] not in [res['id'] for res in final_results]:
                    final_results.append(item)

            # Check if we have enough results
            if len(final_results) < desired_results:
                n *= 2  # Double the results for the next query
                attempt += 1

        return final_results[:desired_results]
    
    def get_metadata_for_id(self, unique_id):
        """
        Retrieve the metadata for a given unique ID from the Chroma collection.

        :param unique_id: The unique ID of the document.
        :return: Metadata for the given ID or None if not found.
        """
        # Use the "get" function to fetch data for the provided unique ID
        results = self.collection.get(ids=[unique_id], include=["metadatas"])

        # Assuming the ID is unique and returns only one match
        if results['metadatas']:
            return results['metadatas'][0]
        return None
    
    def blend_content_with_query(self, original_content, query):
        """
        Blend the user's query with the original content by appending the query to the content.

        :param original_content: The original content of the document.
        :param query: The user's query.
        :return: The blended content.
        """
        return f"{original_content} {query}"

    def reinforce_document_with_query(self, query, unique_id):
        """
        Add a blended version of the user's query and original content as a new document
        with the same metadata as the reinforced document.

        :param query: The user's query that led to positive feedback.
        :param unique_id: The unique ID of the document that received positive feedback.
        """
        # Generate a new unique ID for the reinforced document
        new_uid = str(uuid.uuid4())

        # Retrieve metadata for the reinforced document
        metadatas = self.get_metadata_for_id(unique_id)
        if not metadatas:
            print(f"Error: Could not retrieve metadata for ID {unique_id}")
            return False

        # Blend the user's query with the original content
        blended_content = self.blend_content_with_query(metadatas["content"], query)
        metadatas["content"] = blended_content

        # Update the ID in the metadata to the new UID
        metadatas["id"] = new_uid
        # Optionally, you can add an additional field to indicate this is based on user feedback
        metadatas["type"] = "user_feedback"

        print(metadatas["content"])

        try:
            self.collection.upsert(
                ids=[new_uid],
                documents=[blended_content],  # Use the blended content as the document content
                metadatas=[metadatas]
            )
            return True
        except Exception as e:
            print(f'Error upserting blended content for reinforcement')
            raise e
    
    def count(self):
        return self.collection.count()
