# Project 2

This project is designed to automatically create a set of HITs on Amazon Mechanical Turk for
determining whether a slate of tweets contain COVID misinformation.

# Usage

This program accepts an argument, which is the location of the JSON file containing the tweets.
This file should be in the format produced by the Twitter API. See [example_tweets.json](example_tweets.json)
for details.

```
project2 example_tweets.json
```

By default, it submits HITs to the sandbox environment. However, with the addition of the `-p` flag,
it will instead submit them to the production environment.

```
project2 -p example_tweets.json
```