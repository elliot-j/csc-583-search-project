package edu.arizona.cs;

class ArxivMetadata {
    String id;
    String submitter;
    String authors;
    String title;
    String comments;
    String journal_ref;
    String doi;
    String abstractt;
    String categories;
    Version version;
    String update_date;
    AuthorsParsed authorsParsed;

    public ArxivMetadata(String id, String submitter, String authors, String title, String comments, String journal_ref,
            String doi, String abstractt, String categories, Version version, String update_date,AuthorsParsed authorsParsed) {
        this.id = id;
        this.submitter = submitter;
        this.authors = authors;
        this.title = title;
        this.comments = comments;
        this.journal_ref = journal_ref;
        this.doi = doi;
        this.abstractt = abstractt;
        this.categories = categories;
        this.version = version;
        this.update_date = update_date;
        this.authorsParsed = authorsParsed;
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

    public String getAbstractt() {
      return abstractt;
    }

    public void setAbstractt(String abstractt) {
      this.abstractt = abstractt;
    }

    public String getCategories() {
      return categories;
    }

    public void setCategories(String categories) {
      this.categories = categories;
    }

    public Version getVersion() {
      return version;
    }

    public void setVersion(Version version) {
      this.version = version;
    }

    public String getUpdate_date() {
      return update_date;
    }

    public void setUpdate_date(String update_date) {
      this.update_date = update_date;
    }

    public AuthorsParsed getAuthorsParsed() {
      return authorsParsed;
    }

    public void setAuthorsParsed(AuthorsParsed authorsParsed) {
      this.authorsParsed = authorsParsed;
    }
    
  }