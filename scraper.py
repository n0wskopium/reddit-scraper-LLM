import praw

import json

import os

from dotenv import load_dotenv

  


load_dotenv()

  

def scrape_subreddit(subreddit_name="onepiece", limit=4):
	"""Scrapes top posts from a given subreddit and saves them to a JSON file."""

	try:
		reddit = praw.Reddit(
			client_id=os.getenv("CLIENT_ID"),
			client_secret=os.getenv("CLIENT_SECRET"),
			user_agent=os.getenv("USER_AGENT"),
		)

		subreddit = reddit.subreddit(subreddit_name)

		print(f"🔎 Scraping recent {limit} posts from r/{subreddit_name}...")

		recent_posts = []

		for post in subreddit.new(limit=limit):
			post_data = {
				"id": post.id,
				"title": post.title,
				"text": post.selftext,
				"score": post.score,
				"url": post.url
			}
			recent_posts.append(post_data)

		output_filename = "scraped_posts.json"
		with open(output_filename, "w", encoding="utf-8") as f:
			json.dump(recent_posts, f, indent=4)
		print(f"✅ Successfully saved {len(recent_posts)} posts to {output_filename}")

	except Exception as e:
		print(f"❌ An error occurred during scraping: {e}")

  

if __name__ == "__main__":

    scrape_subreddit()