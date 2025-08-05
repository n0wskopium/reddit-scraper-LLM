# dashboard.py

import os
import csv
import praw
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
@st.cache_resource
def initialize_reddit():
    """Initializes and returns a PRAW instance, cached by Streamlit."""
    print("🚀 Authenticating with Reddit...")
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
        print(f"✅ Authenticated as Reddit user: {reddit.user.me()}")
        return reddit
    except Exception as e:
        st.error(f"Failed to initialize PRAW: {e}")
        return None

def load_tracked_comments(filename='tracked_comments.csv'):
    """Loads the list of tracked comment IDs from the CSV file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header
            return [row[0] for row in reader if row]
    except FileNotFoundError:
        return []

# --- Main UI ---
st.set_page_config(layout="wide", page_title="Reddit Bot Performance Dashboard")
st.title("📊 Reddit Bot Performance Dashboard")
st.markdown("This dashboard shows the live performance of comments posted by the bot.")

reddit = initialize_reddit()

if not reddit:
    st.warning("Could not connect to Reddit. Please check your credentials in the .env file.")
else:
    comment_ids = load_tracked_comments()

    if not comment_ids:
        st.info("No tracked comments found. Please run `main.py` to post a comment first.")
    else:
        st.success(f"Found {len(comment_ids)} tracked comments to analyze.")
        for comment_id in comment_ids:
            try:
                comment = reddit.comment(id=comment_id)
                comment.refresh()
                with st.expander(f"💬 Comment ID: {comment.id} | 👍 Karma: {comment.score}"):
                    
                    st.subheader("Your Original Comment:")
                    st.info(comment.body)
                    
                    st.subheader("Replies Analysis:")
                    
                    replies = comment.replies.list()
                    if not replies:
                        st.write("No replies yet for this comment.")
                    else:
                        for i, reply in enumerate(replies):
                            if reply.author and reply.author.name == reddit.user.me().name:
                                continue
                            
                            st.markdown("---")
                            st.write(f"**Reply from /u/{reply.author.name if reply.author else '[deleted]'}:**")
                            st.write(f"> {reply.body}")
                            heatmap_filename = f"heatmap_adv_{comment_id}_reply_{i+1}.png"
                            if os.path.exists(heatmap_filename):
                                st.image(heatmap_filename, caption=f"Sentiment Heatmap for Reply #{i+1}")
                            else:
                                st.warning(f"Heatmap not found: {heatmap_filename}. Run analysis.py to generate it.")

            except Exception as e:
                st.error(f"Could not fetch data for comment {comment_id}: {e}")
