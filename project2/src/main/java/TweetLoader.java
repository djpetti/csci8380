import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;

/**
 * Handles loading saved tweets and extracting the text.
 */
public class TweetLoader {
    /**
     * Reads the tweet data from a file.
     * @param filePath The path to the JSON file containing an API response.
     * @return The list of tweet text.
     * @throws IOException if the file couldn't be read.
     */
    @org.jetbrains.annotations.NotNull
    public static ArrayList<String> loadTweets(final String filePath) throws IOException {
        final String jsonData = Files.readString(Paths.get(filePath));
        final JSONObject apiResponse = new JSONObject(jsonData);

        // Extract the tweet text.
        final JSONArray tweetData = apiResponse.getJSONArray("data");
        ArrayList<String> tweetsText = new ArrayList<>();
        tweetData.iterator().forEachRemaining(tweet -> {
            String tweetText = ((JSONObject)tweet).getString("text");
            // AMT doesn't handle non-ascii characters very well, so we replace them.
            tweetText = tweetText.replaceAll("[^ -~]", "");

            tweetsText.add(tweetText);
        });

        return tweetsText;
    }
}
