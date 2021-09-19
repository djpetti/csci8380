package com.csci8380.project1;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@Path("/check_names")
public class NameCheckResource {
	
    /**
     * Endpoint that checks if two researchers have a conflict-of-interest.
     * @param firstName The full name of the first researcher.
     * @param secondName The full name of the second researcher.
     * @return JSON response containing conflict information.
     */
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public ConflictCheckResult checkNames(@QueryParam("firstName") String firstName,
                             @QueryParam("secondName") String secondName) {
    	
    	if(!KnowledgeGraph.graphIsLoaded()) {
			String dblpPath = System.getProperty("dblp.path", "dblp-20170124.hdt");
    		try {
    			InputStream input = new FileInputStream(dblpPath);
	    		KnowledgeGraph.load(input);
    		} catch(IOException e) {
    			System.out.println(e);
    		}
    	}
    	
    	// Example JSON response that this endpoint should provide.
        ConflictCheckResult result = new ConflictCheckResult();
        
        List<Paper> papers;
    	if(KnowledgeGraph.graphIsLoaded()) {
            papers = KnowledgeGraph.findCOI(firstName, secondName);
    	} else {
    		papers = new ArrayList<Paper>();
    	}
        
    	switch(papers.size()) {
	    	case 0: result.setLevel(ConflictLevel.NONE); break;
	    	case 1: result.setLevel(ConflictLevel.LOW); break;
	    	case 2: result.setLevel(ConflictLevel.MEDIUM); break;
	    	default: result.setLevel(ConflictLevel.STRONG); break;
    	}
        result.setPapers(papers);

        return result;
    }
}