from sentence_transformers import CrossEncoder
from time import time
import torch


class NeuralReranker:
    def __init__(self, model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"):
        #print(f"Loading reranker model: {model_name}")
        #print(torch.__version__)
        #print(torch.version.cuda)
        #print(f"Cuda available: {torch.cuda.is_available()}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CrossEncoder(model_name, device=device)
        print("Reranker ready!")


    def rerank(self, query: str, documents: list[dict], num_results: int=10) -> list[dict]:
        """Re-ranks documents by semantic relevance to the query.
        Each document must have a 'text' field.
        Returns list sorted from most to least relevant.
        """

        print(f"Reranking {len(documents)} documents")
        print("CrossEncoder device:", self.model.model.device)

        # create pairs (query, text)
        pairs = [(query, doc["text"]) for doc in documents]

        start_time = time()
        # get scores
        scores = self.model.predict(pairs)
        end_time = time()
        print(f"Reranked in {end_time - start_time} seconds")
        # add score for each document
        for doc, score in zip(documents, scores):
            doc["neural_score"] = float(score)

        return sorted(documents, key=lambda x: x["neural_score"], reverse=True)[:num_results]
