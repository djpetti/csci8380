package com.csci8380.project1;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import org.json.JSONArray;
import org.json.JSONObject;

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
    public String checkNames(@QueryParam("firstName") String firstName,
                             @QueryParam("secondName") String secondName) {
        // Example JSON response that this endpoint should provide.
        JSONObject exampleResponse = new JSONObject();
        // Level of conflict. Can be one of "strong", "medium", "low", or "none".
        exampleResponse.put("level", "strong");

        // If there are conflicts, this lists info about conflicting papers.
        // Otherwise, this array should just be empty.
        JSONArray papers = new JSONArray();

        JSONObject paper1 = new JSONObject();
        // Name of the paper.
        paper1.put("name", "Discussions on Things: A Survey");
        // Year paper was published.
        paper1.put("year", 2021);
        // Number of times the paper has been cited.
        paper1.put("citations", 42);

        papers.put(paper1);
        exampleResponse.put("papers", papers);

        return exampleResponse.toString();
    }
}