package edu.arizona.cs;

public class SearchEngineMain{

	/* */
	public static void main(String[] args) throws Exception {
		System.out.println("Welcome to the CSC583 Project");
		//Have this file init everything for indexing and whatnot
		//do not have the search code itself in this file please

		String filePathName = "src\\main\\resources\\arxiv-metadata-oai-snapshot-lite.json";
		JSONReadFromFileTest.readJsonFile(filePathName);		  	   
	}
}

