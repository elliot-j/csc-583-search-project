import datetime
import json
import os
from typing import List
import smart_open
from transformers import AutoModel, AutoTokenizer, DistilBertConfig
import torch
from annoy import AnnoyIndex
from gensim.parsing.preprocessing import remove_stopwords

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
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.vector_length = self.model.config.hidden_size  # setting the vectors used for the annoy index have the same
        # dimensions as the embeddings produced by the transformer model

    def _get_vectors(self, documents: List[str]) -> List[torch.Tensor]:
        """
        Tokenizes a list of documents, passes them through the transformer model, and returns their vectors.
        :param documents: List[str] - A list of documents to convert to vector
        :return: List[torch.Tensor] - A list of torch tensors containing the embeddings of the documents.
        """

        vectors = self.model(**self.tokenizer(documents,padding=True, truncation=True, return_tensors='pt'))
        cls_embedding_vector = [vector[0] for vector in vectors.last_hidden_state]
        return cls_embedding_vector
    def processDocsInBatches(self, documents):
        batchSize = 500
        batchNo = 1 #Left off at batch one
        
        totalBatches = (len(documents) / batchSize ) + 1    
        if os.path.exists(self.index_name):
            self.annoy_index.load(self.index_name)

        #for batchNo in range(0, 1):
                        
        batchStart = batchNo*batchSize
        batchEnd = min(((batchNo+1) * batchSize), len(documents))
        print(f"Processing batch {batchNo} of {int(totalBatches)}. Range {batchStart} to {batchEnd} ||   " + datetime.datetime.now().isoformat())
        batch = documents[batchStart:batchEnd ]
        vectors = self._get_vectors(batch)  # Convert docs to vectors, to represented in vector space.
        for i, normalized_vector in enumerate(vectors):  # Use the normalized vectors to build annoy index.
            self.annoy_index.add_item(i, normalized_vector)  # Adds item i (any nonnegative integer) with vector v.        
        
        self.annoy_index.build(batchSize) 
        self.annoy_index.save(self.index_name)
        
   

    def build_index(self, documents: List[str]):
        """
        Builds an Annoy index based on the vectors of a list of documents.
        :param documents: List[str] - A list of documents to index.
        """        
        self.annoy_index = AnnoyIndex(self.vector_length, "angular")  # angular is the metric.
        self.processDocsInBatches(documents)
         # Build the index, with number of trees = number of documents.
         # Save the index with this filename.

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
        indices, scores = self.annoy_index.get_nns_by_vector(query_vector, n, include_distances=True)
        similar_documents = [(i, documents[i]) for i in indices]
        correctedScores = [(1 - score**2 /2) for score in scores]
        return similar_documents, correctedScores
    def openFile(self, filePath, useForModel = True):
        with smart_open.open(filePath, encoding="utf-8") as f:
            for i, rawLine in enumerate(f):
                if(useForModel):
                    model = json.loads(rawLine)
                    line = model['title'] + " " +model['abstract']
                    yield remove_stopwords(line)
                else:
                    yield remove_stopwords(rawLine)   

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
    # queries = list(nns.openFile(queryFiles, useForModel = False))
    # results = []
    # for i, q in enumerate(queries):
    #     annoyResult, scores = nns.evaluate_query(q,documents)
    #     for j, r in enumerate(annoyResult): 
    #         result = {
    #             'query':q,
    #             'docId':r[0],
    #             'score':scores[j]
    #         }
    #         results.append(result)
    # print("Finished query run - " + datetime.datetime.now().isoformat())
    # json_object = json.dumps(results, indent = 4)

    # print(json_object)
    # with open(resultsFile, "w") as outfile:
    #     outfile.write(json_object)
