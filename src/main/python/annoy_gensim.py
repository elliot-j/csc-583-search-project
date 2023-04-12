import datetime
import json
import os
from re import search
import smart_open
import gensim
from gensim.similarities.annoy import AnnoyIndexer
from gensim.test.utils import get_tmpfile 
from gensim.models.doc2vec import Doc2Vec
from gensim.models.word2vec import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords
import time

class AnnoyIndexerWrapper:
	
	def __init__(self):
		self.model = None
		self.indexer = None
		self.indexFile = 'src/main/resources/annoy_model_gensim.bin'
		self.annoyTrees = 20
		self.docVectorSize = 150
		self.epochs = 20
	def openFile(self, filePath, useForModel = True):
			with smart_open.open(filePath, encoding="utf-8") as f:
				for i, rawLine in enumerate(f):
					if(useForModel):
						model = json.loads(rawLine)
						line = remove_stopwords(model['title'] + " " +model['abstract']);
						tokens = gensim.utils.simple_preprocess(line)
						yield gensim.models.doc2vec.TaggedDocument(tokens, [i])
					else:
						yield remove_stopwords(rawLine)
	
	"""
	Build and train an Annoy Model using GenSim for ease of parsing documents.
	By Default, GenSim uses "angular" similarity metric for the Annoy model as
	seen at https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/similarities/annoy.py

	"""
	def buildAndTrainModel(self, filePath):
		print("loading dataset from file - "  + datetime.datetime.now().isoformat())
		trainSet = list(self.openFile(filePath))
		model = Doc2Vec(vector_size=self.docVectorSize, min_count=1, epochs=self.epochs)
		print("building model vocabulary - " + datetime.datetime.now().isoformat() )
		model.build_vocab(trainSet)
		print("beginning model training - " + datetime.datetime.now().isoformat())
		model.train(trainSet, total_examples=model.corpus_count, epochs=model.epochs)
		print("finished model training - " + datetime.datetime.now().isoformat())
		self.model = model
		self.indexer = AnnoyIndexer(model, self.annoyTrees)			

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
		self.indexer = AnnoyIndexer(self.model, self.annoyTrees)		
	def doesSavedIndexExist(self):
		return os.path.exists(self.indexFile)

searcher =  AnnoyIndexerWrapper()
dataFile = 'src/main/resources/arxiv-metadata-oai-snapshot.json'
queryFiles = 'src/main/resources/lucene-queries.txt'
resultsFile = 'src/main/resources/annoy-results.json'
print(os. getcwd())
if searcher.doesSavedIndexExist():
	print("using existing saved model")
	searcher.loadModel()
else:
	print ("building new model - " + datetime.datetime.now().isoformat())
	searcher.buildAndTrainModel(dataFile)
#result = searcher.queryAnnoy('To appear in Graphs and Combinatorics')
#print('Results for query in format (lineNumber, score) ' + datetime.datetime.now().isoformat())
#print(result)

if (searcher.doesSavedIndexExist() == False):
	print('saving model for future use')
	searcher.saveModel()
queries = list(searcher.openFile(queryFiles, useForModel = False))
results = []
print("Beginning query run - " + datetime.datetime.now().isoformat())
for i, q in enumerate(queries):
	annoyResult = searcher.queryAnnoy(q)
	for j, r in enumerate(annoyResult): 
		result = {
			'query':q,
			'docId':r[0],
			'score':r[1]
		}
		results.append(result)
print("Finished query run - " + datetime.datetime.now().isoformat())
json_object = json.dumps(results, indent = 4)

print(json_object)
with open(resultsFile, "w") as outfile:
    outfile.write(json_object)