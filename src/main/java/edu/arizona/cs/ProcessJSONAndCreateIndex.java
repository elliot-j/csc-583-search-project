package edu.arizona.cs;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;

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
import org.apache.lucene.search.*;
import org.apache.lucene.search.similarities.ClassicSimilarity;
import org.apache.lucene.search.similarities.Similarity;

import java.io.BufferedReader;
import java.io.File;
import java.nio.file.Path;

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
				if(i % 100 == 0){
					System.out.println("Indexing document " + i );
					
				}
				// objects.add(metadata);

				// Index creation for the JSON file which is being Parsed

				// Create a new Lucene document
				Document doc = new Document();

				// Add fields to the document
				doc.add(new StringField("docLine", Integer.toString(i),Field.Store.YES));
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

				doc.add(new StringField("update_date", metadata.getUpdate_date() != null ? metadata.getUpdate_date() : "",
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
	public static void queryForResults(String indexDirectoryPath, String queryFile){
		try(BufferedReader b = new BufferedReader(new FileReader(queryFile))){
			FileWriter queryResults = new FileWriter(new File("src\\main\\resources\\lucene-results.txt"));
			StandardAnalyzer analyzer = new StandardAnalyzer();
			Directory index = FSDirectory.open(Path.of(indexDirectoryPath));
			QueryParser p = new QueryParser("abstract", analyzer);
			IndexReader reader = DirectoryReader.open(index);
			IndexSearcher searcher = new IndexSearcher(reader);
			Similarity s = new ClassicSimilarity();
			searcher.setSimilarity(s);
			String line;
			while((line = b.readLine())!= null){
				System.out.println("Running query: "+line);
				Query q = p.parse(line);
				TopDocs results = searcher.search(q,10);
				for(ScoreDoc d  : results.scoreDocs){
					Document answer = searcher.doc(d.doc);
					String resultLine = String.format("%s,%f,%s,%s\n",line, d.score,answer.getField("title"), answer.getField("abstract") );
					queryResults.append(resultLine);

				}

			}
			queryResults.close();
			index.close();
			

			
		}
		catch(Exception ex){
			System.out.println(ex.toString());
		}

	}
}