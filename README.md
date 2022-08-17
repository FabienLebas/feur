# feur
A French child's game: you answer 'Feur' when someone ends a phrase by 'quoi'. Automated research and answer of tweets via the Twitter API.

In French, hairdresser is said "Coiffeur". "Quoi" means "What". "Feur" means nothing. Children play by answering "Feur" every time someone ends a phrase by "Quoi".
This repo was built as a tutorial for my son to learn Python.
Let me know if you like it and want to use it, what's more: maybe a similar game exists in another language. 

It is indeed a good example to learn Python. Including:
- API calls
- database read / write
- environment variables

Here is how it works:
1- Fetch tweets containing a word ("Quoi" or "Pourquoi" in our example): getTweets
2- Select the tweets ending with the searched word. If "Quoi" is not the last word, then you can't say "Feur": tweetsEligible
3- Check if you have already answered the same tweet: alreadyAnsweredTweets. We use a very simple database: you need only one table called answered_tweets with 4 columns: 
  id: numeric
  answered_tweet: text
  answer_date: timestamp without time zone
  answer_text: text
4- Remove if some of the tweets you fetched were already answered: removeAlreadyAsnweredTweets
5- Answer using Tweepy, a Python library simplifying the usage of the Twitter API: postViaTweepy
6- Save that you have answered: saveIAnswered
7- Process all eligible tweets, one by one: oneBatchOfAnswers

You must have a .env file containing your secrets, in the same format as the example.env file
