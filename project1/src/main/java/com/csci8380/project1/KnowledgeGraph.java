package com.csci8380.project1;

import org.apache.jena.query.*;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.rdfhdt.hdt.hdt.HDT;
import org.rdfhdt.hdt.hdt.HDTManager;
import org.rdfhdt.hdtjena.HDTGraph;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;


public class KnowledgeGraph {
	
	private static HDT hdt;
	private static HDTGraph graph;
	private static Model model;
	
	public static Boolean graphIsLoaded() {
		return model != null;
	}
	
	public static void load(InputStream input) throws IOException {
		/* Load dblp.hdt file */
        KnowledgeGraph.hdt = HDTManager.loadHDT(new BufferedInputStream(input), null);
        KnowledgeGraph.graph = new HDTGraph(hdt, true);
        KnowledgeGraph.model = ModelFactory.createModelForGraph(graph);
	}

    private static List<String> queryGraph(Query query) {
        QueryExecution queryExecution = QueryExecutionFactory.create(query, KnowledgeGraph.model);
        ResultSet resultSet = queryExecution.execSelect();
        List<String> solu_list = new ArrayList<String>();
        while (resultSet.hasNext()) {
        	String next = resultSet.next().toString();
            solu_list.add(next);
        }
        return solu_list;
    }

    public static List<Paper> findCOI(String author_1, String author_2) {
   
        /* Initialize some variables */
        List<String> solutions = new ArrayList<String>(); 
        List<Paper> papers = new ArrayList<Paper>();

        /* SPARQL query sentences */
        Query query_1 = QueryFactory.create(
                "PREFIX elements: <http://purl.org/dc/elements/1.1/>"
                + " PREFIX terms: <http://purl.org/dc/terms/>"
                + " PREFIX foaf: <http://xmlns.com/foaf/0.1/>"
                + " SELECT ?title ?year WHERE {"
                + "  ?paper elements:title ?title ."
                + "  ?paper terms:issued ?year ."
                + "  ?paper foaf:maker ?person1 ."
                + "  ?paper foaf:maker ?person2 ."
                + "  ?person1 foaf:name \"" + author_1 + "\" ."
                + "  ?person2 foaf:name \"" + author_2 + "\" ."
                + "}"
                + " ORDER BY DESC(?year)",
                Syntax.syntaxSPARQL_11
        );

        /* Do query */
        solutions = queryGraph(query_1);

        /* Format output lists */
        for (String element: solutions) {
            String[] splitElement = element.split("\"");
            Paper paper = new Paper();
            paper.setName(splitElement[3]);
            paper.setYear(Integer.parseInt(splitElement[1]));
            papers.add(paper);
        }
        
        System.out.println("Found " + solutions.size() + " conflicts.");

        return papers;
    }

}