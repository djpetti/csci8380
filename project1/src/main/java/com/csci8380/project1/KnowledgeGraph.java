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
        while (resultSet.hasNext())
            solu_list.add(resultSet.next().toString());
        return solu_list;
    }

    public static List<Paper> findCOI(String author_1, String author_2) {
   
        /* Initialize some variables */
        List<String> solutions_1 = new ArrayList<String>();
        List<String> solutions_2 = new ArrayList<String>();
        List<String> solutions = new ArrayList<String>(); 
        List<Paper> papers = new ArrayList<Paper>();

        /* SPARQL query sentences */
        Query query_1 = QueryFactory.create(
                "SELECT ?o1 ?o2 WHERE {?x <http://purl.org/dc/elements/1.1/title> ?o1 . " +
                        "?x <http://purl.org/dc/terms/issued> ?o2 . " +
                        "{SELECT ?x WHERE {?x <http://xmlns.com/foaf/0.1/maker> ?y . " +
                        "{SELECT ?y WHERE {?y <http://xmlns.com/foaf/0.1/name> \"" +
                        author_1 +
                        "\" .}}}}}",
                Syntax.syntaxSPARQL_11
        );
        Query query_2 = QueryFactory.create(
                "SELECT ?o1 ?o2 WHERE {?x <http://purl.org/dc/elements/1.1/title> ?o1 . " +
                        "?x <http://purl.org/dc/terms/issued> ?o2 . " +
                        "{SELECT ?x WHERE {?x <http://xmlns.com/foaf/0.1/maker> ?y . " +
                        "{SELECT ?y WHERE {?y <http://xmlns.com/foaf/0.1/name> \"" +
                        author_2 +
                        "\" .}}}}}",
                Syntax.syntaxSPARQL_11
        );

        /* Do query */
        solutions_1 = queryGraph(query_1);
        solutions_2 = queryGraph(query_2);

        /* Find intersection */
        for (String s: solutions_1)
            if (solutions_2.contains(s))
                solutions.add(s);


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