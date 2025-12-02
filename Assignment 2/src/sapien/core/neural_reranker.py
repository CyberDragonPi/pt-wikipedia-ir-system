from sentence_transformers import CrossEncoder


class NeuralReranker:
    def __init__(self, model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"):
        print(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
        print("Reranker ready!")

    def rerank(self, query: str, documents: list[dict]) -> list[dict]:
        """Re-ranks documents by semantic relevance to the query.
        Each document must have a 'text' field.
        Returns list sorted from most to least relevant.
        """

        # create pairs (query, text)
        pairs = [(query, doc["text"]) for doc in documents]

        # get scores
        scores = self.model.predict(pairs)

        # add score for each document
        for doc, score in zip(documents, scores):
            doc["neural_score"] = float(score)

        return sorted(documents, key=lambda x: x["neural_score"], reverse=True)
