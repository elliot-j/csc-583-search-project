package edu.arizona.cs;

import java.util.List;

import com.google.gson.annotations.SerializedName;

class ArxivMetadata {
    String id;
    String submitter;
    String authors;
    String title;
    String comments;
    @SerializedName("journal-ref")
    String journal_ref;
    String doi;
    
    @SerializedName("report-no")
    String reportNo;

    String license;
    String categories;

    @SerializedName("abstract")
    String paperAbstract;
    
    Version[] versions;
    String update_date;
    @SerializedName("authors_parsed")
    List<String> authorsParsed[];

    public ArxivMetadata(String id, String submitter, String authors, String title, String comments, String journal_ref,
            String doi, String paperAbstract, String categories, Version[] version, String update_date,List<String>[] authorsParsed, String reportNo, String license) {
        this.id = id;
        this.submitter = submitter;
        this.authors = authors;
        this.title = title;
        this.comments = comments;
        this.journal_ref = journal_ref;
        this.doi = doi;
        this.paperAbstract = paperAbstract;
        this.categories = categories;
        this.versions = version;
        this.update_date = update_date;
        this.authorsParsed = authorsParsed;
        this.reportNo = reportNo;
        this.license = license;
    }

    public String getId() {
      return id;
    }

    public void setId(String id) {
      this.id = id;
    }

    public String getSubmitter() {
      return submitter;
    }

    public void setSubmitter(String submitter) {
      this.submitter = submitter;
    }

    public String getAuthors() {
      return authors;
    }

    public void setAuthors(String authors) {
      this.authors = authors;
    }

    public String getTitle() {
      return title;
    }

    public void setTitle(String title) {
      this.title = title;
    }

    public String getComments() {
      return comments;
    }

    public void setComments(String comments) {
      this.comments = comments;
    }

    public String getJournal_ref() {
      return journal_ref;
    }

    public void setJournal_ref(String journal_ref) {
      this.journal_ref = journal_ref;
    }

    public String getDoi() {
      return doi;
    }

    public void setDoi(String doi) {
      this.doi = doi;
    }

    public String getAbstract() {
      return paperAbstract;
    }

    public void setAbstract(String paperAbstract) {
      this.paperAbstract = paperAbstract;
    }

    public String getCategories() {
      return categories;
    }

    public void setCategories(String categories) {
      this.categories = categories;
    }

    public Version[] getVersions() {
      return versions;
    }

    public void setVersions(Version[] version) {
      this.versions = version;
    }

    public String getUpdate_date() {
      return update_date;
    }

    public void setUpdate_date(String update_date) {
      this.update_date = update_date;
    }

    public List<String>[] getAuthorsParsed() {
      return authorsParsed;
    }

    public void setAuthorsParsed(List<String>[] authorsParsed) {
      this.authorsParsed = authorsParsed;
    }
    public String getLicense() {
      return license;
    }

    public void setLicense(String license) {
      this.license = license;
    }
    public String getReportNo() {
      return reportNo;
    }

    public void setReportNo(String reportNo) {
      this.reportNo = reportNo;
    }
  }