package edu.arizona.cs;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.LinkedList;

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
          System.out.println("Abstract: "+ metadata.getAbstract());
          System.out.println("categories: " + metadata.getCategories());
          System.out.println("Version: " + metadata.getVersions());
          System.out.println("Update Date: "+ metadata.getUpdate_date());
          System.out.println("Authors Parsed: "+ metadata.getAuthorsParsed());
          objects.add(metadata);
        }
       
    } catch(Exception e) {
        e.printStackTrace();
    }
   }
  }