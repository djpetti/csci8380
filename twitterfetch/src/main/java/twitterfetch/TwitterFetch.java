package twitterfetch;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import org.apache.commons.lang3.StringEscapeUtils;

import twitter4j.Query;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;

public class TwitterFetch {
	
	private static String convertTweetToJson(Status tweet) {
		return "{" 
				+ "\"created_at\":\"" + tweet.getCreatedAt() + "\","
				+ "\"id\":\"" + tweet.getId() + "\","
				+ "\"text\":\"" + StringEscapeUtils.escapeJava(tweet.getText()) + "\""
				+ "}";
	}
	
	private static String convertTweetsToJson(List<Status> list) {
		String finalString = "{\"data\":[";
		Date oldestDate = new Date();
		long oldestId = 0;
		@SuppressWarnings("deprecation")
		Date newestDate = new Date(0, 0, 0, 0, 0, 0);
		long newestId = 0;
		for(Status tweet : list) {
			finalString += convertTweetToJson(tweet) + ",";
			if(tweet.getCreatedAt().before(oldestDate)) {
				oldestDate = tweet.getCreatedAt();
				oldestId = tweet.getId();
			} 
			if(tweet.getCreatedAt().after(newestDate)) {
				newestDate = tweet.getCreatedAt();
				newestId = tweet.getId();
			}
		}
		if(list.size() > 0) {
			// Remove the last comma if it got placed there.
			finalString = finalString.substring(0, finalString.length() - 1);
		}
		finalString += "],\"meta\":{ "
					+ "\"newest_id\":\"" + newestId + "\","
					+ "\"oldest_id\":\"" + oldestId + "\","
					+ "\"result_count\": " + list.size()
					+ "}}";
		return finalString;
		
	}


	public static void main(String[] args) throws TwitterException, IOException {
		
		Twitter twitter = TwitterFactory.getSingleton();
		
		// https://www.cureus.com/articles/28976-coronavirus-goes-viral-quantifying-the-covid-19-misinformation-epidemic-on-twitter
		// This research shoed that the keywords reporting the highest amount of information were #2019_ncov and #Corona. Others were selected on intuition.
		Query query = new Query("#antivax OR #Corona OR #2019_ncov");
		query.setLang("en");
		
		// Code was retrieved from https://stackoverflow.com/questions/18800610/how-to-retrieve-more-than-100-results-using-twitter4j
		// We use this code as a workaround since Twitter4j only allows for up to 100 tweets at a time.
		// The code circumvents this by polling again after the first is completed.
		int numberOfTweets = 512;
		long lastID = Long.MAX_VALUE;
		List<Status> tweets = new ArrayList<Status>();
		while (tweets.size () < numberOfTweets) {
			if (numberOfTweets - tweets.size() > 100)
				query.setCount(100);
			else 
				query.setCount(numberOfTweets - tweets.size());
			try {
				QueryResult result = twitter.search(query);
				tweets.addAll(result.getTweets());
				for (Status t: tweets) 
					if(t.getId() < lastID) lastID = t.getId();

			}

			catch (TwitterException te) {
				te.printStackTrace();
			}; 
			query.setMaxId(lastID - 1);
		}
		  
		BufferedWriter writer = new BufferedWriter(new FileWriter("antivax.json"));
		writer.write(convertTweetsToJson(tweets));
		writer.close();
		
	}

}
