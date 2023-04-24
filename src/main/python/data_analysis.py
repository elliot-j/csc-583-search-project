
from gensim.models import KeyedVectors
import datetime
import json
import os
from re import search
import smart_open
import gensim
import numpy as np
from gensim.similarities.annoy import AnnoyIndexer
from gensim.test.utils import get_tmpfile ,datapath
from gensim.models.doc2vec import Doc2Vec
from gensim.models.word2vec import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.scripts.glove2word2vec import glove2word2vec
from collections import Counter
import pandas

from .DataFilePaths import DataFilePaths


dataFile =  DataFilePaths.OriginalDataSet
glove_file = 'src/main/resources/glove.6B.300d.txt'
processedGlovFile = 'src/main/resources/glove.6B.300d_gensim.txt'

def openFile( filePath, isPreProcessed=True):
	with smart_open.open(filePath, encoding="utf-8") as f:
		jsonData = json.load(f)
		if isPreProcessed:
			for i, rawLine in enumerate(jsonData):
				tokens = gensim.utils.simple_preprocess(rawLine)
				yield tokens
		else: 
			for i, rawLine in enumerate(f):							
				yield remove_stopwords(rawLine)
def addUnknownTokenEmbeddingsToGlove():
	unk_tok = '[UNK]'
	pad_tok = '[PAD]'

	# initialize the new embedding values
	unk_emb = glove.vectors.mean(axis=0)
	pad_emb = np.zeros(300)

	# add new embeddings to glove
	glove.add_vectors([unk_tok, pad_tok], [unk_emb, pad_emb])

	# get token ids corresponding to the new embeddings
	unk_id = glove.key_to_index[unk_tok]
	pad_id = glove.key_to_index[pad_tok]

def count_unknown_words(data, vocabulary):
    counter = Counter()
    for row in data:
        counter.update(tok for tok in row if tok not in vocabulary)
    return counter
def getTermStatistics(train_df, glove):
	# find out how many times each unknown token occurrs in the corpus
	c = count_unknown_words(train_df['tokens'], glove.key_to_index)

	# find the total number of tokens in the corpus
	total_tokens = train_df['tokens'].map(len).sum()

	# find some statistics about occurrences of unknown tokens
	unk_tokens = sum(c.values())
	percent_unk = unk_tokens / total_tokens
	distinct_tokens = len(list(c))

	print(f'total number of tokens: {total_tokens:,}')
	print(f'number of unknown tokens: {unk_tokens:,}')
	print(f'number of distinct unknown tokens: {distinct_tokens:,}')
	print(f'percentage of unkown tokens: {percent_unk:.2%}')
	print('top 50 unknown words:')
	for token, n in c.most_common(10):
		print(f'\t{n}\t{token}')
def loadGlove():
	print("loading glove from file - " + datetime.datetime.now().isoformat())
	if(os.path.exists(processedGlovFile) == False):
		glove2word2vec(glove_file, processedGlovFile)
	glove = KeyedVectors.load_word2vec_format(processedGlovFile)			
	print("finished loading glove from file - " + datetime.datetime.now().isoformat())
	return glove

def loadDataSet():
	print("loading dataset from file - " + datetime.datetime.now().isoformat())
	train_df = pandas.read_json(dataFile)
	print("finished reading dataset from file - " + datetime.datetime.now().isoformat())
	#train_df['tokens'] = gensim.utils.simple_preprocess(train_df[0])#
	#train_df['tokens'] = train_df.apply(lambda row: gensim.utils.simple_preprocess(row[0]), axis=1)
	return train_df

#train_df = loadDataSet()
glove = loadGlove()
#getTermStatistics(train_df, glove)