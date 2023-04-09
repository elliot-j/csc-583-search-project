package edu.arizona.cs;

import java.io.File;

public class SearchEngineMain{

	/* */
	public static void main(String[] args) throws Exception {
		System.out.println("Welcome to the CSC583 Project");
		//Have this file init everything for indexing and whatnot
		//do not have the search code itself in this file please

		String filePathName = "src\\main\\resources\\arxiv-metadata-oai-snapshot.json";
		String indexPath = "src\\main\\resources\\lucene_index.bin";
		String queryFile = "src\\main\\resources\\lucene-queries.txt";
		File indexFile = new File(indexPath);
		if(!indexFile.exists()){
			indexFile.createNewFile();
			System.out.println("Index not found, recreating from data file");
			ProcessJSONAndCreateIndex.readJsonFile(filePathName,indexPath);		  	   
			ProcessJSONAndCreateIndex.queryForResults(indexPath,queryFile);
		} else {
			System.out.println("Index found, running queries for results");
			ProcessJSONAndCreateIndex.queryForResults(indexPath,queryFile);

		}
	}
}

