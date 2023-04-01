package edu.arizona.cs;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.LinkedList;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;

public class JSONReadFromFileTest {

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
          //System.out.println("Authors Parsed: "+ metadata.getAuthorsParsed());
          objects.add(metadata);
        }
       
    } catch(Exception e) {
        e.printStackTrace();
    }
   }
  }