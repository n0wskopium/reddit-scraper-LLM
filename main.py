# main.py

import os
import json
import praw
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load all environment variables from .env file
load_dotenv()

def post_comment_to_reddit(post_id, comment_text):
    """Logs into Reddit using credentials from .env and posts a comment."""
    print("\n🚀 Authenticating with Reddit to post...")
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
        
        submission = reddit.submission(id=post_id)
        new_comment = submission.reply(body=comment_text)
        
        print(f"✅ Successfully posted comment! Comment ID: {new_comment.id}")
        return new_comment.id
        
    except Exception as e:
        print(f"❌ An error occurred while posting to Reddit: {e}")
        return None

def track_comment(comment_id):
    """Saves the ID of a successfully posted comment to a CSV file for analysis."""
    tracking_file = 'tracked_comments.csv'
    # Check if file exists to write header
    file_exists = os.path.isfile(tracking_file)
    
    with open(tracking_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['comment_id', 'post_date']) # Write header
        writer.writerow([comment_id, datetime.now().isoformat()])
    print(f"📝 Comment ID {comment_id} saved to {tracking_file} for future analysis.")

def review_and_post_workflow(filename="posts_with_replies.json"):
    """Main workflow to review, edit, and post generated replies."""
    
    # 1. Load the posts with their generated replies
    try:
        with open(filename, "r", encoding="utf-8") as f:
            posts_with_replies = json.load(f)
        if not posts_with_replies:
            print("No replies found in the file. Exiting.")
            return
    except FileNotFoundError:
        print(f"❌ Error: The file '{filename}' was not found. Run llm_handler.py first.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from {filename}.")
        return

    # 2. Iterate through each post for review
    for i, post in enumerate(posts_with_replies):
        current_reply = post['generated_reply']
        
        while True: # Loop for editing a single reply
            print("\n" + "=" * 80)
            print(f"Reviewing Post {i+1}/{len(posts_with_replies)}")
            print(f"📝 Title: {post['title']}")
            print("-" * 40)
            print("🤖 Generated Reply:")
            print(f"   \"{current_reply}\"")
            print(f"   (Word count: {len(current_reply.split())})")
            print("-" * 40)

            # 3. Ask for user action
            choice = input("Choose an action: [a]ccept, [e]dit, [r]eject, [s]kip to next? ").lower()

            if choice == 'a':
                # Accept and post
                print("✅ Reply accepted. Posting to Reddit...")
                comment_id = post_comment_to_reddit(post['id'], current_reply)
                if comment_id:
                    track_comment(comment_id)
                break # Move to the next post in the list

            elif choice == 'e':
                # Edit the reply
                print("✏️ Enter your new reply. Press Enter on an empty line when done.")
                new_reply_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    new_reply_lines.append(line)
                
                current_reply = "\n".join(new_reply_lines)
                print("📝 Reply updated. Please review your edits.")
                continue # Re-display the same post with the edited reply

            elif choice == 'r' or choice == 's':
                # Reject or Skip
                print("⏩ Skipping this post.")
                break # Move to the next post

            else:
                print("⚠️ Invalid choice. Please try again.")

    print("\n🎉 Review workflow completed!")

if __name__ == "__main__":
    # First, ensure replies are generated (optional, you can run llm_handler.py separately)
    # from llm_handler import generate_replies_from_file
    # generate_replies_from_file()
    
    # Now, start the review process
    review_and_post_workflow()
