import os
from re import search
import smart_open
import gensim
from gensim.similarities.annoy import AnnoyIndexer
from gensim.test.utils import get_tmpfile 
from gensim.models.doc2vec import Doc2Vec


class AnnoyIndexerWrapper:
	
	def __init__(self):
		self.model = None
		self.indexer = None
		self.indexFile = 'src/main/resources/annoy_model_gensim.bin'
	def openFile(self, filePath):
			with smart_open.open(filePath, encoding="utf-8") as f:
				for i, line in enumerate(f):
					tokens = gensim.utils.simple_preprocess(line)
					yield gensim.models.doc2vec.TaggedDocument(tokens, [i])
	
	"""
	Build and train an Annoy Model using GenSim for ease of parsing documents.
	By Default, GenSim uses "angular" similarity metric for the Annoy model as
	seen at https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/similarities/annoy.py

	"""
	def buildAndTrainModel(self, filePath):
		trainSet = list(self.openFile(filePath))
		model = Doc2Vec(vector_size=50, min_count=1, epochs=100)
		model.build_vocab(trainSet)
		model.train(trainSet, total_examples=model.corpus_count, epochs=model.epochs)
		self.model = model
		self.indexer = AnnoyIndexer(model, 2)			
		
	def queryAnnoy(self, queryString):
		if(self.model == None or self.indexer == None):
			raise "You must build a model first by calling buildAndTrainModel"
		queryTokens = gensim.utils.simple_preprocess(queryString)
		queryVector = self.model.infer_vector(queryTokens)
		# Both query methods return the same result
		#result = self.model.dv.most_similar([queryVector],topn=10, indexer=self.indexer)		
		result = self.indexer.most_similar(queryVector, 10)
		return result

	def saveModel(self):
		fname = self.indexFile
		file = open(fname, 'wb')
		print("saving model to " + fname)
		if self.model != None:
			self.model.save(file)
	def loadModel(self):
		fname = self.indexFile
		print("loading model from " + fname)
		self.model = Doc2Vec.load(fname)
		self.indexer = AnnoyIndexer(self.model, 2)		
	def doesSavedIndexExist(self):
		return os.path.exists(self.indexFile)

searcher =  AnnoyIndexerWrapper()
dataFile = 'src/main/resources/arxiv-metadata-oai-snapshot-lite.json'
print(os. getcwd())
if searcher.doesSavedIndexExist():
	print("using existing saved model")
	searcher.loadModel()
else:
	print ("building new model")
	searcher.buildAndTrainModel(dataFile)

result = searcher.queryAnnoy('To appear in Graphs and Combinatorics')
print('Results for query in format (lineNumber, score)')
print(result)

if (searcher.doesSavedIndexExist() == False):
	print('saving model for future use')
	searcher.saveModel()
