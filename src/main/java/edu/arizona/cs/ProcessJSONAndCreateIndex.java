package edu.arizona.cs;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.store.Directory;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;

import org.apache.lucene.search.*;
import org.apache.lucene.search.similarities.ClassicSimilarity;
import org.apache.lucene.search.similarities.Similarity;
import java.lang.reflect.Type;
import com.google.gson.reflect.TypeToken;
import java.io.BufferedReader;
import java.io.File;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedList;

import org.apache.lucene.store.FSDirectory;

/*
  * Process a JSON file
  * Create an index
  * Add documents to the index
  * Commit the changes and close the index
*/

public class ProcessJSONAndCreateIndex {

	public static void readJsonFile(String filePathName, String indexDirectoryPath) throws FileNotFoundException {
		JsonReader reader = new JsonReader(new FileReader(filePathName));
		reader.setLenient(true);

		try {
			StandardAnalyzer analyzer = new StandardAnalyzer();
			Directory index = FSDirectory.open(Path.of(indexDirectoryPath));
			IndexWriterConfig config = new IndexWriterConfig(analyzer);
			IndexWriter indexWriter = new IndexWriter(index, config);
			int i = 0;
			while (reader.hasNext()) {
				ArxivMetadata metadata = new Gson().fromJson(reader, ArxivMetadata.class);
				if (i % 100 == 0) {
					System.out.println("Indexing document " + i);

				}
				// objects.add(metadata);

				// Index creation for the JSON file which is being Parsed

				// Create a new Lucene document
				Document doc = new Document();

				// Add fields to the document
				doc.add(new StringField("docLine", Integer.toString(i), Field.Store.YES));
				doc.add(new StringField("id", metadata.getId() != null ? metadata.getId() : "",
						Field.Store.YES));
				doc.add(new TextField("submitter", metadata.getSubmitter() != null ? metadata.getSubmitter() : "",
						Field.Store.YES));
				doc.add(new TextField("authors", metadata.getAuthors() != null ? metadata.getAuthors() : "",
						Field.Store.YES));
				doc.add(new TextField("title", metadata.getTitle() != null ? metadata.getTitle() : "",
						Field.Store.YES));
				
				doc.add(new TextField("comments", metadata.getComments() != null ? metadata.getComments() : "",
						Field.Store.YES));
				doc.add(new TextField("journal_ref", metadata.getJournal_ref() != null ? metadata.getJournal_ref() : "",
						Field.Store.YES));
				doc.add(new TextField("doi", metadata.getDoi() != null ? metadata.getDoi() : "",
						Field.Store.YES));
				doc.add(new TextField("report_no", metadata.getReportNo() != null ? metadata.getReportNo() : "",
						Field.Store.YES));
				doc.add(new TextField("license", metadata.getLicense() != null ? metadata.getLicense() : "",
						Field.Store.YES));
				doc.add(new TextField("abstract", metadata.getAbstract() != null ? metadata.getAbstract() : "",
						Field.Store.YES));
				
				doc.add(new TextField("categories", metadata.getCategories() != null ? metadata.getCategories() : "",
						Field.Store.YES));
				doc.add(new StringField("raw_abstract", metadata.getAbstract() != null ? metadata.getAbstract() : "",
						Field.Store.YES));						
				doc.add(new StringField("raw_title", metadata.getTitle() != null ? metadata.getTitle() : "",
				Field.Store.YES));


				doc.add(new StringField("update_date",
						metadata.getUpdate_date() != null ? metadata.getUpdate_date() : "",
						Field.Store.YES));
				// Add the document to the Lucene index
				indexWriter.addDocument(doc);
				i++;// record line number for use with Annoy to ID documents
			}
			indexWriter.commit();
			indexWriter.close();

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public static void queryForResults(String indexDirectoryPath, String queryFile, String outfile) {
		try (BufferedReader b = new BufferedReader(new FileReader(queryFile))) {
			FileWriter queryResultsWriter = new FileWriter(new File(outfile));
			StandardAnalyzer analyzer = new StandardAnalyzer();
			Directory index = FSDirectory.open(Path.of(indexDirectoryPath));
			//QueryParser p = new QueryParser("abstract", analyzer);
			IndexReader reader = DirectoryReader.open(index);
			IndexSearcher searcher = new IndexSearcher(reader);
			Similarity s = new ClassicSimilarity();
			//searcher.setSimilarity(s);
			LinkedList<FullResult> jsonResults = new LinkedList<FullResult>();
			String line;
			String [] fields = new String[]{"abstract", "title"};
			MultiFieldQueryParser p  = new MultiFieldQueryParser( fields,analyzer );
			while ((line = b.readLine()) != null) {
				System.out.println("Running query: " + line);
				Query q = p.parse(line);
				TopDocs results = searcher.search(q, 10);
				for (ScoreDoc d : results.scoreDocs) {
					Document answer = searcher.doc(d.doc);
					FullResult r = new FullResult();
					r.score = (double)d.score;
					r.docId = Integer.parseInt(answer.getField("docLine").stringValue());
					r.query = line;
					r.paperAbstract = answer.getField("raw_abstract").stringValue();
					r.title = answer.getField("raw_title").stringValue();					
					jsonResults.add(r);

				}

			}
			Gson gson = new GsonBuilder().create();
    		gson.toJson(jsonResults, queryResultsWriter);
			queryResultsWriter.close();
			index.close();

		} catch (Exception ex) {
			System.out.println(ex.toString());
		}

	}

	public static ArrayList<ScoredResult> ResolveFullAnnoyDocument(String indexDirectoryPath, String annoyResultJsonFile, String outfileName) {
		try {
			JsonReader jsonReader = new JsonReader(new FileReader(annoyResultJsonFile));
			jsonReader.setLenient(true);
			Type listType = new TypeToken<ArrayList<ScoredResult>>() {}.getType(); 
			ArrayList<ScoredResult> annoyResults = new Gson().fromJson(jsonReader, listType);
			LinkedList<FullResult> fullResult = new LinkedList<FullResult>();

			//load lucene index
			FileWriter queryResultsWriter = new FileWriter(new File(outfileName));
			StandardAnalyzer analyzer = new StandardAnalyzer();
			Directory index = FSDirectory.open(Path.of(indexDirectoryPath));
			QueryParser p = new QueryParser("docLine", analyzer);
			IndexReader reader = DirectoryReader.open(index);
			IndexSearcher searcher = new IndexSearcher(reader);
			Similarity s = new ClassicSimilarity();
			// searcher.setSimilarity(s);

			for(int i = 0; i < annoyResults.size(); ++i){
				Query q = p.parse(Integer.toString(annoyResults.get(i).docId));
				TopDocs results = searcher.search(q, 1);
				for (ScoreDoc d : results.scoreDocs) {
					Document answer = searcher.doc(d.doc);
					
					FullResult result = new FullResult(annoyResults.get(i));

					result.title = answer.getField("raw_title").stringValue();
					result.paperAbstract =  answer.getField("raw_abstract").stringValue();
					fullResult.add(result);					

				}
			}
			
			Gson gson = new GsonBuilder().create();
    		gson.toJson(fullResult, queryResultsWriter);
			queryResultsWriter.close();

			return annoyResults;
		} catch (Exception e) {
			System.out.println(e);
			return null;

		}

	}
}