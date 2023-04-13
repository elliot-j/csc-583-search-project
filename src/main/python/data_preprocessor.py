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

def openFile(self, filePath, useForModel = True):
	with smart_open.open(filePath, encoding="utf-8") as f:
		for i, rawLine in enumerate(f):
			if(useForModel):
				model = json.loads(rawLine)
				line = model['title'] + " " +model['abstract']
				yield remove_stopwords(line)
			else:
				yield rawLine    
dataFile = 'src/main/resources/arxiv-metadata-oai-snapshot.json'
outFile =  'src/main/resources/processed-arxiv-metadata-oai-snapshot.json'
results = list(openFile(dataFile))
json_object = json.dumps(results, indent = 4)

print(json_object)
with open(outFile, "w") as f:
	f.write(json_object)