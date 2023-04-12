import datetime
import json
import os
from typing import List
import smart_open
from transformers import AutoModel, AutoTokenizer, DistilBertConfig
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
        config = DistilBertConfig(max_position_embeddings  = 768)
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
        # vectors = [None] * len(documents)
        # i = 0
        # for document in documents:
        #     # tokens = (self.tokenizer(document, return_tensors="pt")).input_ids.squeeze()
        #     # if len(tokens) > 512: 
        #     #     tokens = tokens[:512]
        #     # encoding  = self.model(**tokens)[0].detach().squeeze()
        #     # vectors[i] = encoding
        #     # i = i + 1
        #     tokens = self.tokenizer(document, return_tensors="pt",truncation  = True)
        #     if(tokens.input_ids.shape[1]  > 512):
        #         print('large document found')
        #     encoding = self.model(**tokens)[0].detach().squeeze()    
        #     vectors[i] = encoding
        #     i = i + 1        
        vectors = [
            self.model(**self.tokenizer(document, return_tensors="pt",truncation  = True))[0].detach().squeeze()
            for document in documents
        ]
        averaged_vectors = [torch.mean(vector, dim=0) for vector in vectors]
        return averaged_vectors
    
   

    def build_index(self, documents: List[str]):
        """
        Builds an Annoy index based on the vectors of a list of documents.
        :param documents: List[str] - A list of documents to index.
        """
        vectors = self._get_vectors(documents)  # Convert docs to vectors, to represented in vector space.
        self.annoy_index = AnnoyIndex(self.vector_length, "angular")  # angular is the metric.
        for i, normalized_vector in enumerate(vectors):  # Use the normalized vectors to build annoy index.
            self.annoy_index.add_item(i, normalized_vector)  # Adds item i (any nonnegative integer) with vector v.
        self.annoy_index.build(len(documents))  # Build the index, with number of trees = number of documents.
        self.annoy_index.save(self.index_name)  # Save the index with this filename.

    def evaluate_query(self, query: str, documents: List[str], n: int = 10) -> List[str]:
        """
        Finds the n most similar documents to a given query.
        :param query: str - The query document.
        :param documents: List[str] - A list of documents to index.
        :param n: int - The number of similar documents to retrieve. Default is 10.
        :return: List[str] - A list of index and documents for n most similar results to the query.
        """
        if not os.path.exists(self.index_name):
            raise FileNotFoundError("Annoy index does not exists, Call build_index().")

        query_vector = self._get_vectors([query])[0]
        indices, scores = self.annoy_index.get_nns_by_vector(query_vector, n)
        similar_documents = [(i, documents[i]) for i in indices]
        correctedScores = [(1 - score**2 /2) for score in scores]
        return similar_documents, correctedScores
    def openFile(self, filePath, useForModel = True):
        with smart_open.open(filePath, encoding="utf-8") as f:
            for i, rawLine in enumerate(f):
                if(useForModel):
                    model = json.loads(rawLine)
                    line = model['title'] + " " +model['abstract']
                    yield line
                else:
                    yield rawLine    

if __name__ == "__main__":
    """
    This is just a sample on how the code would look like with dummy documents.
    """
    dataFile = 'src/main/resources/arxiv-metadata-oai-snapshot.json'
    queryFiles = 'src/main/resources/lucene-queries.txt'
    resultsFile = 'src/main/resources/annoy-results_transformer.json'

    nns = NearestNeighborSearcher("src/main/resources/arxiv_transformer_index.bin")

    print("loading dataset from file - "  + datetime.datetime.now().isoformat())
    documents = list(nns.openFile(dataFile))    
    print("finished loading dataset from file - "  + datetime.datetime.now().isoformat())
    print("loaded " + str(len(documents))+ " items")
    nns.build_index(documents)

    # query = "Stirling cycle numbers counts" ## found in doc #3
    # results, scores = nns.evaluate_query(query, documents) 
    # print(scores)
    # print(results)
    queries = list(nns.openFile(queryFiles, useForModel = False))
    results = []
    for i, q in enumerate(queries):
        annoyResult, scores = nns.evaluate_query(q,documents)
        for j, r in enumerate(annoyResult): 
            result = {
                'query':q,
                'docId':r[0],
                'score':scores[j]
            }
            results.append(result)
    print("Finished query run - " + datetime.datetime.now().isoformat())
    json_object = json.dumps(results, indent = 4)

    print(json_object)
    with open(resultsFile, "w") as outfile:
        outfile.write(json_object)
