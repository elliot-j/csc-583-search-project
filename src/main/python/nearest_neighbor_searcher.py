import os
from typing import List
from transformers import AutoModel, AutoTokenizer
import torch
from annoy import AnnoyIndex


class NearestNeighborSearcher:
    """
    Class that creates the vector of the documents, and builds an annoy index, parses the query
    and returns resulting documents relevant to the query.
    """
    def __init__(self, index_name: str = "annoy_index.ann"):
        """
        Initializes the NearestNeighborSearcher object with a pre-trained transformer model.
        """
        self.annoy_index = None
        self.index_name = index_name
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.model = AutoModel.from_pretrained("distilbert-base-uncased")
        self.vector_length = self.model.config.hidden_size  # setting the vectors used for the annoy index have the same
        # dimensions as the embeddings produced by the transformer model

    def _get_vectors(self, documents: List[str]) -> List[torch.Tensor]:
        """
        Tokenizes a list of documents, passes them through the transformer model, and returns their vectors.
        :param documents: List[str] - A list of documents to convert to vector
        :return: List[torch.Tensor] - A list of torch tensors containing the embeddings of the documents.
        """
        vectors = [
            self.model(**self.tokenizer(document, return_tensors="pt"))[0].detach().squeeze()
            for document in documents
        ]
        return vectors

    def _get_normalized_vectors(self, vectors: List[torch.Tensor]) -> List[torch.Tensor]:
        """
        Computes the center for each document / query by veraging the points and finding the center.
        :param vectors: List[torch.Tensor] - A list of torch tensors containing the embeddings of the documents / query.
        :return: List[torch.Tensor] - A list of torch tensors containing the avg embeddings of the documents / query.
        """
        averaged_vectors = [torch.mean(vector, dim=0) for vector in vectors]
        return averaged_vectors

    def build_index(self, documents: List[str]):
        """
        Builds an Annoy index based on the vectors of a list of documents.
        :param documents: List[str] - A list of documents to index.
        """
        vectors = self._get_vectors(documents)  # Convert docs to vectors, to represented in vector space.
        normalized_vectors = self._get_normalized_vectors(vectors)  # Normalize the length of the vector.
        self.annoy_index = AnnoyIndex(self.vector_length, "angular")  # angular is the metric.
        for i, normalized_vector in enumerate(normalized_vectors):  # Use the normalized vectors to build annoy index.
            self.annoy_index.add_item(i, normalized_vector)  # Adds item i (any nonnegative integer) with vector v.
        self.annoy_index.build(len(documents))  # Build the index, with number of trees = number of documents.
        self.annoy_index.save(self.index_name)  # Save the index with this filename.

    def evalulate_query(self, query: str, documents: List[str], n: int = 10) -> List[str]:
        """
        Finds the n most similar documents to a given query.
        :param query: str - The query document.
        :param documents: List[str] - A list of documents to index.
        :param n: int - The number of similar documents to retrieve. Default is 10.
        :return: List[str] - A list of index and documents for n most similar results to the query.
        """
        if not os.path.exists(self.index_name):
            raise FileNotFoundError("Annoy index does not exists, Call build_index().")

        query_vector = self._get_normalized_vectors(self._get_vectors([query]))[0]
        indices = self.annoy_index.get_nns_by_vector(query_vector, n)
        similar_documents = [(i, documents[i]) for i in indices]
        return similar_documents


if __name__ == "__main__":
    """
    This is just a sample on how the code would look like with dummy documents.
    """
    nns = NearestNeighborSearcher("sample_annoy_index.ann")
    documents = [
        "That restaurant was not as good as the last movie I watched.",
        "I'm selling a used car in good condition",
        "Food was okay, the rest so so",
        "I love cats, but don't really like hyenas",
        "On the road, you must be careful",
        "That eatery called Raddichio sells good food and wine",
        "That eatery called Tamarindo sells bad and tasteless food",
        "You should come to my hotel, our chef makes amazing food"
    ]
    nns.build_index(documents)
    query = "that restaurant where I can get good food "
    results = nns.evalulate_query(query, documents)  # Gets the top 10 results, but since the documents are just 8, it
    # retrieves the top 8 results.
    print(results)
    """
    [(5, 'That eatery called Raddichio sells good food and wine'),
     (7, 'You should come to my hotel, our chef makes amazing food'),
      (6, 'That eatery called Tamarindo sells bad and tasteless food'),
       (0, 'That restaurant was not as good as the last movie I watched.'),
        (2, 'Food was okay, the rest so so'),
         (1, "I'm selling a used car in good condition"),
          (3, "I love cats, but don't really like hyenas"),
           (4, 'On the road, you must be careful')]
    """
