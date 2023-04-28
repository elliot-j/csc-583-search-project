import math
import smart_open
import json


	
def computeNormalizedGain(data):
	dgc =0
	for i, value in enumerate(data):
		val = value['userScore']
		pos = i + 1
		dgc +=  val / math.log(pos+1, 2)
	
	#data.sort(reverse=True)
	sortedData = sorted(data, key= lambda x : x['userScore'], reverse = True)

	idgc =0
	for i, value in enumerate(sortedData):
		val = value['userScore']
		pos = i + 1
		idgc +=  val / math.log(pos+1, 2)
	if idgc == 0:
		return 0 
	return dgc/idgc



with smart_open.open('results/complete-annoy-results-transformer.json', encoding="utf-8") as f:
	transformerData = json.load(f)
with smart_open.open('results/lucene-results-bm25v2.json', encoding="utf-8") as f:
	bm25Data = json.load(f)
with smart_open.open('results/lucene-results-tfidf.json', encoding="utf-8") as f:
	tfData = json.load(f)	
print("Annoy NDCG SCores")
for q in range(0, 31):
	lower = q*10
	upper = ((q+1) * 10 ) 
	#print(f"({lower}, {upper})")
	rRange = range(lower, upper)
	results = []
	for index in rRange:
		
		results.append(transformerData[index])	
	#print(f"computing NDCG measure for query {q+1}")
	print(f"Query {q+1} - {round(computeNormalizedGain(results), 3)}")
print("BM25 NDCG SCores")
for q in range(0, 31):
	lower = q*10
	upper = ((q+1) * 10 ) 
	#print(f"({lower}, {upper})")
	rRange = range(lower, upper)
	results = []
	for index in rRange:
		
		results.append(bm25Data[index])	
	#print(f"computing NDCG measure for query {q+1}")
	print(f"Query {q+1} - {round(computeNormalizedGain(results), 3)}")

print("TF-IDF  NDCG SCores")
for q in range(0, 31):
	lower = q*10
	upper = ((q+1) * 10 ) 
	#print(f"({lower}, {upper})")
	rRange = range(lower, upper)
	results = []
	for index in rRange:
		
		results.append(tfData[index])	
	#print(f"computing NDCG measure for query {q+1}")
	print(f"Query {q+1} - {round(computeNormalizedGain(results), 3)}")


# ## Map scored results from BD25 on to TFIDF
# for q in range(0, 31):
# 	lower = q*10
# 	upper = ((q+1) * 10 ) 
# 	#print(f"({lower}, {upper})")
# 	rRange = range(lower, upper)
# 	for j in rRange:
# 		bmResult = bm25Data[j]
# 		for i in rRange: 			
# 			if bmResult['docId'] == tfData[i]['docId'] :
# 				tfData[i]['userScore'] = bmResult['userScore'] 
# 				tfData[i]['isBm25'] = True

# bm25UserScores = json.dumps(bm25Data)
# with open('results/lucene-results-bm25v2.json', "w") as f:
# 		f.write(bm25UserScores)

# tfUserScores = json.dumps(tfData)
# with open('results/lucene-results-tfidf.json', "w") as f:
# 		f.write(tfUserScores)		

