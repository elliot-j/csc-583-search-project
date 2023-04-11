package edu.arizona.cs;

public class FullResult extends ScoredResult{
	public FullResult(){}
	public FullResult(ScoredResult r){
		this.docId =r.docId;
		this.query = r.query;
		this.score = r.score;
	}
	public String title;
	public String paperAbstract;
}
