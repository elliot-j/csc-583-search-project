import math
import smart_open
import json


	
def computeNormalizedGain(data):
	dgc =0
	for i, value in enumerate(data):
		val = value['userScore']
		pos = i + 1
		dgc +=  val / math.log(pos+1, 2)
	
	sortedData = sorted(data, key= lambda x : x['userScore'], reverse = True)

	idgc =0
	for i, value in enumerate(sortedData):
		val = value['userScore']
		pos = i + 1
		idgc +=  val / math.log(pos+1, 2)
	if idgc == 0:
		return 0 
	return dgc/idgc
def computeGainForResultSet(dataSet):
	sum = 0 
	for q in range(0, 31):
		lower = q*10
		upper = ((q+1) * 10 ) 
		rRange = range(lower, upper)
		results = []
		for index in rRange:
			
			results.append(dataSet[index])	
		#print(f"computing NDCG measure for query {q+1}")
		gain = round(computeNormalizedGain(results), 3)
		sum += gain
		print(f"{gain}")
	print(f"average {sum/31}")
with smart_open.open('results/complete-annoy-results-transformer.json', encoding="utf-8") as f:
	transformerData = json.load(f)

print("Annoy NDCG SCores")
computeGainForResultSet(transformerData)

with smart_open.open('results/lucene-results-bm25v2.json', encoding="utf-8") as f:
	bm25Data = json.load(f)	
print("BM25 NDCG SCores")
computeGainForResultSet(bm25Data)

with smart_open.open('results/lucene-results-tfidf.json', encoding="utf-8") as f:
	tfData = json.load(f)	
print("TF-IDF  NDCG SCores")
computeGainForResultSet(tfData)
