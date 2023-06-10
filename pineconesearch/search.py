"""
   Created on Fri Jun 09 2023
   Copyright (c) 2023 Subramanya N
"""
import logging
import pinecone

logger = logging.getLogger(__name__)


class PineConeSearch:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, pinecone_index: str):
        """Initialize PineConeSearch class

        Args:
            pinecone_api_key (str): Pinecone API key
            pinecone_env (str): Pinecone environment to use
            pinecone_index (str): Pinecone index to use
        """
        # initialize Pinecone API
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(index_name=pinecone_index)
        logger.info(self.index.describe_index_stats())

    def upsert_documents(self, documents: list):
        """Upsert documents into the Pinecone index

        Args:
            documents (list): List of documents to upsert
        """
        self.index.upsert(vectors=documents)

    def delete_documents(self):
        """Delete all documents from the Pinecone index"""
        self.index.delete(deleteAll="true")

    def query(self, query_vector: list, top_k: int = 5):
        """Query the Pinecone index

        Args:
            query_vector (list): Query vector
            top_k (int, optional): Number of results to return. Defaults to 5.

        Returns:
            dict: Query response
        """
        return self.index.query(
            vector=query_vector, top_k=top_k, include_metadata=True, include_values=True
        )

    def query_and_combine(
        self, query_vector: list, top_k: int = 5, threshold: float = 0.75
    ):
        """Query Pinecone index and combine responses to string

        Args:
            query_embedding (list): Query embedding
            index (str): Pinecone index to query
            top_k (int, optional): Number of top results to return. Defaults to 5.
            threshold(int, optional): Similarity Threshold. Defaults to 0.75

        Returns:
            str: Combined responses
        """
        responses = self.query(query_vector=query_vector, top_k=top_k)
        _responses = []
        for sample in responses["matches"]:
            if sample["score"] < threshold:
                continue
            if "text" in sample["metadata"]:
                _responses.append(sample["metadata"]["text"])
            else:
                _responses.append(str(sample["metadata"]))

        return " \n --- \n ".join(_responses).replace("\n---\n", " \n --- \n ").strip()
