package edu.arizona.cs;

public class Version {
    String version;
    String created;
    
    public Version(String version, String created) {
        this.version = version;
        this.created = created;
    }
    
    public String getVersion() {
        return version;
    }
    public void setVersion(String version) {
        this.version = version;
    }
    public String getCreated() {
        return created;
    }
    public void setCreated(String created) {
        this.created = created;
    }
   
}
