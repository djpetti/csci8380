package com.csci8380.project1;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

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
        // Example JSON response that this endpoint should provide.
        ConflictCheckResult result = new ConflictCheckResult();
        result.setLevel(ConflictLevel.STRONG);

        List<Paper> papers = new ArrayList<>();
        Paper paper = new Paper();
        paper.setName("Discussions on Things: A Survey");
        paper.setYear(2021);
        paper.setCitations(42);

        papers.add(paper);
        result.setPapers(papers);

        return result;
    }
}