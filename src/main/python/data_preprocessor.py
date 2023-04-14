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


def openFile(filePath, phase):
	maxTokens = 0
	with smart_open.open(filePath, encoding="utf-8") as f:
		if (phase == 'stopwords'):
			for i, rawLine in enumerate(f):
				model = json.loads(rawLine)
				line = model['title'] + " " + model['abstract']
				# yield  {'tokens':gensim.utils.simple_preprocess()}
				yield remove_stopwords(line.lower())
		elif (phase == 'tokens'):
			jsonData = json.load(f)
			for i, rawLine in enumerate(jsonData):
				tokens = {'tokens':gensim.utils.simple_preprocess(rawLine) }
				maxTokens = max(len(tokens['tokens']), maxTokens)
				yield tokens
	print (f"Longest token sequence = {maxTokens}")

dataFile = 'src/main/resources/arxiv-metadata-oai-snapshot.json'
stopWordsOutFile = 'src/main/resources/stopwords-arxiv-metadata-oai-snapshot.json'
tokensOutFile = 'src/main/resources/tokens-arxiv-metadata-oai-snapshot.json'

phase = 'stopwords'

## longest token sequence = 165

if (phase == 'stopwords'):
	print("loading dataset from file - " + datetime.datetime.now().isoformat())
	results = list(openFile(dataFile, phase))
	print("finished dataset from file - " + datetime.datetime.now().isoformat())
	json_object = json.dumps(results, indent=None)
	with open(stopWordsOutFile, "w") as f:
		f.write(json_object)
elif (phase == 'tokens'):
	print("loading dataset from file - " + datetime.datetime.now().isoformat())
	results = list(openFile(stopWordsOutFile, phase))
	print("finished dataset from file - " + datetime.datetime.now().isoformat())
	json_object = json.dumps(results, indent=None)
	with open(tokensOutFile, "w") as f:
		f.write(json_object)
