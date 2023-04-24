import datetime
import json
import os
from typing import List
import smart_open
from transformers import AutoModel, AutoTokenizer
import torch
from annoy import AnnoyIndex
from gensim.parsing.preprocessing import remove_stopwords
import torch.nn.functional as F
from termcolor import colored
from DataFilePaths import DataFilePaths
torch.device('cpu')
class NearestNeighborSearcher:
    """
    Class that creates the vector of the documents, and builds an annoy index, parses the query
    and returns resulting documents relevant to the query.
    """
    def __init__(self,batchSize,  index_name):
        """
        Initializes the NearestNeighborSearcher object with a pre-trained transformer model.
        """
        self.annoy_index = None
        self.index_name = index_name
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.vector_length = self.model.config.hidden_size  # setting the vectors used for the annoy index have the same
        self.batchSize = batchSize
        self.totalBatches = None
        self.failedBatches = []
        # dimensions as the embeddings produced by the transformer model

    def mean_pooling(self, model_output, attention_mask):
        """
        Pool CLS Embedding Tensors to vectors so we can index them with Annoy. 
        Sourced from https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 
        """
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    def _get_vectors(self, documents: List[str]) -> List[torch.Tensor]:
        """
        Tokenizes a list of documents or queries, passes them through the transformer model, and returns their vectors.
        :param documents: List[str] - A list of documents to convert to vector
        :return: List[torch.Tensor] - A list of torch tensors containing the embeddings of the documents.
        """
        tokens = self.tokenizer(documents,padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            vectors = self.model(**tokens)
        ## shape of last hidden state (sentence, layer, embedding)
        sentence_embeddings = self.mean_pooling(vectors, tokens['attention_mask'])
        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        #cls_embedding_vector = [vector.last_hidden_state[0][0] for vector in vectors]
        return sentence_embeddings
  
    def processDocsInBatches(self, documents, totalBatches = None):
        """
        Process Embedding files saved to disk and load them into an Annoy Index
        If totalBatches is specified, will only process that number of batches 
        to facilitate debugging
        """ 
                
        batchOutDir = DataFilePaths.ModelEmbeddingBatchFolder
        if totalBatches == None:
            totalBatches = int((len(documents) / self.batchSize ) + 1    )

        if os.path.exists(self.index_name):
            self.annoy_index.load(self.index_name)
        for batchNo in range(0, totalBatches):
            batchFile = f'{batchOutDir}/{self.batchSize}__{batchNo}.batch'
            if(os.path.exists(batchFile) == False):
                print(colored(f'batch {batchNo+1} not found. Skipping', 'red'))
                continue
            print(f"Processing batch {batchNo+1} of {int(totalBatches)}. ||   " + datetime.datetime.now().isoformat())
            batchStart = batchNo*self.batchSize
            try:
                vectors = torch.load(batchFile,map_location=torch.device('cpu'))
                for i, embedding in enumerate(vectors) :
                    if(i ==0):
                        print(f'annoy index item starts at {batchStart+i}')
                    self.annoy_index.add_item(batchStart+i, embedding)
                print(f"Finished Processing batch {batchNo+1} of {int(totalBatches)}. ||   " + datetime.datetime.now().isoformat())
            except Exception as e: 
                print(colored(f"Failed Processing batch {batchNo+1} of {int(totalBatches)} ||   " + datetime.datetime.now().isoformat(), 'red'))
                print(e)
                self.failedBatches.append(batchNo)
        print('building annoy index')
        self.annoy_index.build(200) 
        print(f"saving index to {self.index_name}")
        self.annoy_index.save(self.index_name)

    def processTokensToEmbeddings(self, documents):
        """
        Convert a list of documents to Normalized CLS Embedding vectors in batches and save the 
        generated vectors to disk for later indexing in the event of a crash. If a batch
        has already been save to disk, that batch will be skipped
        """    
        #batchNo = 0 #Left off at batch one
        batchOutDir = DataFilePaths.ModelEmbeddingBatchFolder
        #totalBatches = int((len(documents) / self.batchSize ) + 1    )
        if totalBatches == None:
            totalBatches = int((len(documents) / self.batchSize ) + 1    )

        for batchNo in range(0, totalBatches):
            batchFile = f'{batchOutDir}/{self.batchSize}__{batchNo}.batch'
            if(os.path.exists(batchFile)):
                print(f'batch {batchNo+1} already processed. Skipping')
                continue
            batchStart = batchNo*self.batchSize
            batchEnd = min(((batchNo+1) * self.batchSize), len(documents)) -1
            if(batchStart >= len(documents)):
                print(f"{batchNo} exists on disk already")
                break
            try:
                print(f"Processing batch {batchNo+1} of {int(totalBatches)}. Range {batchStart} to {batchEnd} ||   " + datetime.datetime.now().isoformat())
                batch = documents[batchStart:batchEnd  ]
                vectors = self._get_vectors(batch)  # Convert docs to vectors, to represented in vector space.
                print(f"Writing batch {batchNo+1} to {batchFile} ||   " + datetime.datetime.now().isoformat())
                f = open(batchFile, "x")
                torch.save(vectors,batchFile)			
                print(f"Finished Processing batch {batchNo+1} of {int(totalBatches)}. Range {batchStart} to {batchEnd} ||   " + datetime.datetime.now().isoformat())
            except Exception as e: 
                print(colored(f"Failed Processing batch {batchNo+1} of {int(totalBatches)}. Range {batchStart} to {batchEnd} ||   " + datetime.datetime.now().isoformat(), 'red'))
                print(e)
                self.failedBatches.append(batchNo)

            
    """
    Generate the Annoy Index from pre-computed embeddings
    """
    def build_index(self, documents: List[str],totalBatches = None):
        """
        Builds an Annoy index based on the vectors of a list of documents.
        :param documents: List[str] - A list of documents to index.
        """        
        self.annoy_index = AnnoyIndex(self.vector_length, "angular")  # angular is the metric.
        self.processDocsInBatches(documents,totalBatches)
         # Build the index, with number of trees = number of documents.
         # Save the index with this filename.
    """
    Evaluate a query against the Annoy Index. Will load the annoy index 
    from a file if one has been previously saved. 

    Returns a tuple of the matched document IDs and their cosine similarity scores
    """
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
        if self.annoy_index == None:
            self.annoy_index = AnnoyIndex(self.vector_length, "angular")  # angular is the metric.
            self.annoy_index.load(self.index_name)

        query_vector = self._get_vectors([query])[0]
        indices, scores = self.annoy_index.get_nns_by_vector(query_vector, n, include_distances=True)
        similar_documents = [(i, documents[i]) for i in indices]
        correctedScores = [(1 - score**2 /2) for score in scores]
        return similar_documents, correctedScores
    

if __name__ == "__main__":

    now = datetime.datetime.now()
    dataFile = DataFilePaths.OriginalDataSet
    queryFiles = DataFilePaths.QueriesFile
    #resultsFile = f'src/main/resources/results/annoy-results_transformer__{now.hour}_{now.minute}_{now.second}.json'
    resultsFile = DataFilePaths.TransformerResultsOutputFile
    tokenizedDataFile = DataFilePaths.DataSetWithoutStopwords
    nns = NearestNeighborSearcher(batchSize=250, index_name=DataFilePaths.AnnoyTransformerIndexFile)

    print("loading dataset from file - "  + datetime.datetime.now().isoformat())
    documents = list(DataFilePaths.openFile(tokenizedDataFile,isTokenized=True))    
    print("finished loading dataset from file - "  + datetime.datetime.now().isoformat())
    print("loaded " + str(len(documents))+ " items")

    ##Uncomment this line to generate the document embeddings 
    ## Disabled by default due to the amount of time this takes
    #nns.processTokensToEmbeddings(documents)
    
    ## Uncomment this line to build a new Annoy Index
    ## using pre-computed embeddings
    # nns.build_index(documents, totalBatches = None)
    # print("Failed on batches")
    # print(nns.failedBatches)

    ## evaluate_query will load a saved Annoy Index if
    ## you have already built one using build_index
    queries = list(DataFilePaths.openFile(queryFiles, isPreProcessed = False))
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

    print(f'writing results to {resultsFile}')
    with open(resultsFile, "w") as outfile:
        outfile.write(json_object)
