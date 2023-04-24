package edu.arizona.cs;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;

public class SearchEngineMain {

	/* */
	public static void main(String[] args) throws Exception {
		System.out.println("Welcome to the CSC583 Project");
		// Have this file init everything for indexing and whatnot
		// do not have the search code itself in this file please

		String filePathName = "src\\main\\resources\\arxiv-metadata-oai-snapshot.json";
		String indexPath = "src\\main\\resources\\lucene_index.bin";
		String queryFile = "src\\main\\resources\\lucene-queries.txt";
		String annoyResult = "src\\main\\resources\\results\\annoy-results_transformer.json";
		String luceneResult = "src\\main\\resources\\results\\lucene-results-bm25v2.json";
		String resolvedResult = "src\\main\\resources\\results\\complete-annoy-results-transformer.json";
		File indexFile = new File(indexPath);

		boolean luceneQueryRun = false;
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		try {
			System.out.println("Enter 'A' to resolve documents from an Annoy Index result. Enter 'L' to build a lucene index or run queries against a pre-built index");
			
			String command = br.readLine();
			if(command.toLowerCase().equals("a"))
				luceneQueryRun = false;
			else if(command.toLowerCase().equals("l"))
				luceneQueryRun = true;
			else System.out.println("No valid command entered");
		} catch (Exception ioe) {
			System.out.println(ioe);
			return;
		}
		if (luceneQueryRun) {
			System.out.println("Running Queries against Lucene Index");
			if (!indexFile.exists()) {
				System.out.println("Index not found, recreating from data file");
				ProcessJSONAndCreateIndex.readJsonFile(filePathName, indexPath);
				ProcessJSONAndCreateIndex.queryForResults(indexPath, queryFile,luceneResult);
				System.out.println("Results written to " + luceneResult);
			} else {
				System.out.println("Index found, running queries for results");
				ProcessJSONAndCreateIndex.queryForResults(indexPath, queryFile, luceneResult);
				System.out.println("Results written to " + luceneResult);

			}
		} else{
			System.out.println("Looking up original documents from Annoy Index Result");
			ProcessJSONAndCreateIndex.ResolveFullAnnoyDocument(indexPath, annoyResult,resolvedResult);
			System.out.println("Results written to " + resolvedResult);
		}

	}
}
