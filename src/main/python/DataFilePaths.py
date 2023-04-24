import json
import smart_open
from gensim.parsing.preprocessing import remove_stopwords

class DataFilePaths:
	OriginalDataSet = 'src/main/resources/arxiv-metadata-oai-snapshot.json'
	QueriesFile = 'src/main/resources/lucene-queries.txt'
	TransformerResultsOutputFile = 'src/main/resources/results/annoy-results_transformer.json'
	Doc2VecResultsOutputFile ="src/main/resources/annoy-results_doc2vec.json"
	DataSetWithoutStopwords = 'src/main/resources/stopwords-arxiv-metadata-oai-snapshot.json'
	DataSetAsWordTokens = 'src/main/resources/tokens-arxiv-metadata-oai-snapshot.json'
	AnnoyTransformerIndexFile = "src/main/resources/models/arxiv_transformer_index.bin"
	Doc2VecModelFile = "src/main/resources/annoy_model_gensim.bin"
	ModelEmbeddingBatchFolder = 'src/main/resources/batches'


	def openFile( filePath, isPreProcessed=True, isTokenized = False):
		with smart_open.open(filePath, encoding="utf-8") as f:
			
			if isPreProcessed:
				jsonData = json.load(f)
				for i, rawLine in enumerate(jsonData):
					if(isTokenized == False):
						tokens = gensim.utils.simple_preprocess(rawLine)
					else: tokens = rawLine
					yield tokens
			else: 
				for i, rawLine in enumerate(f):							
					yield remove_stopwords(rawLine)