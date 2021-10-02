import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.mturk.AmazonMTurk;
import com.amazonaws.services.mturk.AmazonMTurkClientBuilder;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * The main class for all project 2 code.
 */
public class Project2 {
    /**
     * Endpoint for the Mechanical Turk sandbox.
     */
    private static final String SANDBOX_ENDPOINT = "mturk-requester-sandbox.us-east-1.amazonaws.com";
    /**
     * Endpoint for production Mechanical Turk.
     */
    private static final String PROD_ENDPOINT = "https://mturk-requester.us-east-1.amazonaws.com";
    /**
     * Region to use for Mechanical Turk.
     */
    private static final String SIGNING_REGION = "us-east-1";

    /**
     * Location of the XML template file.
     */
    private static final String XML_TEMPLATE = "templates/question.xml";
    /**
     * Location of the HTML template file.
     */
    private static final String HTML_TEMPLATE = "templates/covid_question.html";

    /**
     * Prints a usage message and exits the program.
     */
    private static void printUsageAndExit() {
        System.out.println("""
                Usage:
                 program2 [-p] tweets.json
                 \t-p: Use the production instead of the sandbox environment.
                 """);
        System.exit(1);
    }

    /**
     * @return A client for the Mechanical Turk sandbox.
     */
    private static AmazonMTurk getSandboxClient() {
        AmazonMTurkClientBuilder builder = AmazonMTurkClientBuilder.standard();
        builder.setEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(SANDBOX_ENDPOINT, SIGNING_REGION));
        return builder.build();
    }

    /**
     * @return A client for the Mechanical Turk production environment.
     */
    private static AmazonMTurk getProdClient() {
        AmazonMTurkClientBuilder builder = AmazonMTurkClientBuilder.standard();
        builder.setEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(PROD_ENDPOINT, SIGNING_REGION));
        return builder.build();
    }

    public static void main(final String @NotNull [] args) {
        if (args.length != 1 && args.length != 2) {
            printUsageAndExit();
        }

        String tweetFile = args[0];
        Boolean useProduction = args[0].equals("-p");
        if (useProduction) {
            tweetFile = args[1];
        }

        // Load the tweets from the file.
        ArrayList<String> tweets;
        try {
            tweets = TweetLoader.loadTweets(tweetFile);
        } catch (IOException e) {
            System.err.println("Could not read from file: " + tweetFile);
            printUsageAndExit();
            return;
        }

        // Create the actual HITs.
        final AmazonMTurk client = useProduction ? getProdClient() : getSandboxClient();
        HitCreator hitCreator = new HitCreator(client);
        TemplateHitMaker templateHitMaker;
        try {
            templateHitMaker = new TemplateHitMaker(XML_TEMPLATE, HTML_TEMPLATE, hitCreator, useProduction);
        } catch (IOException e) {
            System.err.println("Could not read from template file: " + XML_TEMPLATE);
            printUsageAndExit();
            return;
        }

        for (final String tweet : tweets) {
            final Map<String, String> templateValues = new HashMap<>();
            templateValues.put("tweet_text", tweet);

            final HitCreator.HITInfo hitInfo = templateHitMaker.createHit(templateValues);
            System.out.println("Created HIT with ID " + hitInfo.getHITId());
        }
    }
}
