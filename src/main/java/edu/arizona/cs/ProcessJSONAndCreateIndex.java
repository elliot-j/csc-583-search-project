package edu.arizona.cs;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.LinkedList;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.ByteBuffersDirectory;
import org.apache.lucene.index.IndexWriterConfig;


/*
  * Process a JSON file
  * Create an index
  * Add documents to the index
  * Commit the changes and close the index
*/

public class ProcessJSONAndCreateIndex {

    public static void readJsonFile(String filePathName) throws FileNotFoundException {
      JsonReader reader = new JsonReader(new FileReader(filePathName));
      reader.setLenient(true);
      LinkedList<ArxivMetadata> objects = new LinkedList<ArxivMetadata>();
      try {
        
        while(reader.hasNext()) {
          ArxivMetadata metadata = new Gson().fromJson(reader, ArxivMetadata.class);
          System.out.println("Reading JSON from a file");
          System.out.println("----------------------------");
          System.out.println("Id: "+metadata.getId());
          System.out.println("Submitter: " + metadata.getSubmitter());
          System.out.println("Authors: " +metadata.getAuthors());
          System.out.println("Title: " + metadata.getTitle());
          System.out.println("Comments: " + metadata.getComments());
          System.out.println("Journal-Ref: " + metadata.getJournal_ref());
          System.out.println("doi: " + metadata.getDoi());
          System.out.println("Report-No: " + metadata.getReportNo());
          System.out.println("License: " + metadata.getLicense());
          System.out.println("Abstract: "+ metadata.getAbstract());
          System.out.println("categories: " + metadata.getCategories());
          Version[] versions = metadata.getVersions();
          for (int i = 0; i < versions.length; i++) {
              System.out.println("Version " + i + ": " + versions[i].getVersion());
              System.out.println("Created " + i + ": " + versions[i].getCreated());
              System.out.println();
          }
          System.out.println("Update Date: "+ metadata.getUpdate_date());

          List<String>[] authorsParsed = metadata.getAuthorsParsed();
          for (int i = 0; i < authorsParsed.length; i++) {
            System.out.println("Author " + (i + 1) + ":");
            for (int j = 0; j < authorsParsed[i].size(); j++) {
                System.out.println("  " + authorsParsed[i].get(j));
            }
        }
          objects.add(metadata);

          //Index creation for the JSON file which is being Parsed
          StandardAnalyzer analyzer = new StandardAnalyzer();
          Directory index = new ByteBuffersDirectory();
          IndexWriterConfig config = new IndexWriterConfig(analyzer);
          try (IndexWriter indexWriter = new IndexWriter(index, config)) {
            // Create a new Lucene document
            Document doc = new Document();

            // Add fields to the document
            doc.add(new StringField("id", metadata.getId(), Field.Store.YES));
            doc.add(new TextField("submitter", metadata.getSubmitter(), Field.Store.YES));
            doc.add(new TextField("authors", metadata.getAuthors(), Field.Store.YES));
            doc.add(new TextField("title", metadata.getTitle(), Field.Store.YES));
            doc.add(new TextField("comments", metadata.getComments(), Field.Store.YES));
            doc.add(new TextField("journal_ref", metadata.getJournal_ref(), Field.Store.YES));
            doc.add(new TextField("doi", metadata.getDoi(), Field.Store.YES));
            doc.add(new TextField("report_no", metadata.getReportNo(), Field.Store.YES));
            doc.add(new TextField("license", metadata.getLicense(), Field.Store.YES));
            doc.add(new TextField("abstract", metadata.getAbstract(), Field.Store.YES));
            doc.add(new TextField("categories", metadata.getCategories(), Field.Store.YES));
            Version[] versionss = metadata.getVersions();
            for (int k = 0; k < versions.length; k++) {
                doc.add(new TextField("version", versionss[k].getVersion(), Field.Store.YES));
                doc.add(new TextField("created", versionss[k].getCreated(), Field.Store.YES));
            }
            doc.add(new TextField("update_date", metadata.getUpdate_date(), Field.Store.YES));

            List<String>[] authorsParsedd = metadata.getAuthorsParsed();
            for (int i = 0; i < authorsParsedd.length; i++) {
                for (int j = 0; j < authorsParsedd[i].size(); j++) {
                    doc.add(new TextField("author_parsed", authorsParsedd[i].get(j), Field.Store.YES));
                }
            }

            // Add the document to the Lucene index
            indexWriter.addDocument(doc);
            indexWriter.commit();
            indexWriter.close();
          }
        }
       
    } catch(Exception e) {
        e.printStackTrace();
    }
   }
  }