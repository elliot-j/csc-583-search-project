import json
from collections import defaultdict


def parse_file(file_path):
    """
    Parse the json file
    :param file_path: path of the json file, the results
    :return:
    """
    with open(file_path, 'r') as file:
        json_string = file.read()
    data = json.loads(json_string)
    return data


def group_by_query(data_lucene, data_bm25):
    """
    Group both the results using query so query string should be exact same in both.
    :param data_lucene: data parsed from lucene result json
    :param data_bm25: data parsed from bm25 result json
    :return: grouped data by query
    """
    grouped_data = defaultdict(lambda: {'lucene': [], 'bm25': []})

    for entry in data_lucene:
        grouped_data[entry['query']]['lucene'].append(entry)

    for entry in data_bm25:
        grouped_data[entry['query']]['bm25'].append(entry)

    return grouped_data


def calculate_ensemble_score(entries_lucene, entries_bm25, lambda_value=36.1):
    """
    Calculate ensemble score using lambda_value
    :param entries_lucene:
    :param entries_bm25:
    :return:
    """
    scores = {}

    for entry in entries_lucene:
        doc_id = entry['docId']
        score = entry['score']
        scores[doc_id] = {'lucene': score, 'bm25': 0}

    for entry in entries_bm25:
        doc_id = entry['docId']
        score = entry['score']
        if doc_id in scores:
            scores[doc_id]['bm25'] = score
        else:
            scores[doc_id] = {'lucene': 0, 'bm25': score}

    ensemble_scores = {}
    for doc_id, score_data in scores.items():
        ensemble_score = score_data['lucene'] + (lambda_value * score_data['bm25'])
        ensemble_scores[doc_id] = ensemble_score
    return ensemble_scores


def save_sorted_results_to_json(ensemble_scores_by_query, output_file):
    """
    Save the sorted score value in descending order
    :param ensemble_scores_by_query:
    :param output_file:
    :return:
    """
    with open(output_file, 'w') as file:
        json.dump(ensemble_scores_by_query, file, indent=2)


def get_min_max_ensemble_scores(ensemble_scores_by_query):
    """
    Get the mix max ensemble score
    :param ensemble_scores_by_query: the final ensemble_scores_by_query
    :return:
    """
    all_scores = [entry["ensembleScore"] for query_results in ensemble_scores_by_query.values() for entry in
                  query_results]
    min_score = min(all_scores)
    max_score = max(all_scores)
    return min_score, max_score


def calculate_mrr(ensemble_scores_by_query, golden_documents):
    """
    Calculate the MRR
    :param ensemble_scores_by_query:
    :param golden_documents: the list of golden documents for each 31 query
    :return:
    """
    reciprocal_ranks = []
    for query, golden_doc_id in zip(ensemble_scores_by_query.keys(), golden_documents):
        results = ensemble_scores_by_query[query]
        position = -1
        for idx, result in enumerate(results):
            if str(result["docId"]) == golden_doc_id:
                position = idx + 1
                break
        if position != -1:
            reciprocal_ranks.append(1 / position)
        else:
            reciprocal_ranks.append(0)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    return mrr


if __name__ == "__main__":
    data_file_lucene = "lucene-results-bm25.json"
    data_file_bm25 = "complete-annoy-results-query-name-combined.json"
    data_lucene = parse_file(data_file_lucene)
    data_bm25 = parse_file(data_file_bm25)
    grouped_data = group_by_query(data_lucene, data_bm25)
    ensemble_scores_by_query = {}
    for query, entries in grouped_data.items():
        ensemble_scores = calculate_ensemble_score(entries['lucene'], entries['bm25'], lambda_value = 36.1)
        sorted_results = sorted(ensemble_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_results_json = [{"docId": doc_id, "ensembleScore": score} for doc_id, score in sorted_results]
        ensemble_scores_by_query[query] = sorted_results_json
    print(f"[min, max] ensemble score = {get_min_max_ensemble_scores(ensemble_scores_by_query)}")
    golden_documents = ["133869", "1945581", "1027458", "1218574", "205807", "1046961", "1410596", "723621", "2154967",
                        "480172", "12151555", "517193", "1790898", "361214", "1636233", "468086", "1118514", "1255935",
                        "1373649", "267908", "1014444", "1171904", "1661826", "1697177", "93477", "62262", "1824309",
                        "1174207", "1584628", "521466", "2205489"]
    mrr = calculate_mrr(ensemble_scores_by_query, golden_documents)
    print("Mean Reciprocal Rank (MRR) using the ensemble method:", mrr)
    output_file = "sorted_ensemble_scores_by_query.json"
    save_sorted_results_to_json(ensemble_scores_by_query, output_file)
