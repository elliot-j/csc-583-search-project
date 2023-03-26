package edu.arizona.cs;

public class SearchEngineMain{

	/* */
	public static void main(String[] args) throws Exception {
		System.out.println("Hello World");
		//Have this file init everything for indexing and whatnot
		//do not have the search code itself in this file please

		String filePathName = "D:\\CSC583_Project\\csc-583-search-project\\src\\resources\\arxiv-metadata-oai-snapshot.json";
		JSONReadFromFileTest.readJsonFile(filePathName);		  	   
	}
}

