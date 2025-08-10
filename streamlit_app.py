# streamlit_app.py (Corrected and Unified)

import streamlit as st
import os
import csv
import json
import datetime
import time # Added for better UI feedback
from scraper import scrape_subreddit
from llm_handler import generate_replies_from_file
from analysis import analyze_comment_performance, initialize_reddit, initialize_sentiment_pipeline, visualize_reply_sentiment
import praw # Added for performance dashboard

# --- Utility Functions (from various files) ---

def load_posts_with_replies(filename="posts_with_replies.json"):
    """Load posts with replies from JSON file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tracked_comment(comment_id, post_id, reply_text):
    """Save tracked comment to CSV file."""
    file_exists = os.path.exists('tracked_comments.csv')
    try:
        with open('tracked_comments.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['comment_id', 'post_id', 'reply_text', 'timestamp'])
            writer.writerow([comment_id, post_id, reply_text, datetime.datetime.now().isoformat()])
        return True
    except Exception as e:
        st.error(f"Failed to save tracked comment: {e}")
        return False

def post_comment_to_reddit(reddit_instance, post_id, reply_text):
    """Post comment to Reddit and return comment ID."""
    try:
        submission = reddit_instance.submission(id=post_id)
        comment = submission.reply(reply_text)
        return comment.id
    except Exception as e:
        st.error(f"❌ Error posting comment: {str(e)}")
        return None

def load_tracked_comments(filename='tracked_comments.csv'):
    """Loads the list of tracked comment IDs from the CSV file."""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            return [row[0] for row in reader if row]
    except Exception:
        return []

# --- Streamlit Page Implementations ---

def page_home():
    """Home page with project overview and status."""
    st.header("🏠 Welcome to the Reddit AI Bot Control Panel!")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Project Workflow")
        st.markdown("""
        1.  **Scrape Subreddit**: Extracts recent posts from a chosen subreddit.
        2.  **Generate Replies**: Uses a large language model to create replies for the scraped posts.
        3.  **Review & Post**: Manually review, edit, and approve replies to be posted on Reddit.
        4.  **View Performance**: A live dashboard to track the karma and replies to your bot's comments.
        """)
    with col2:
        st.subheader("📂 File Status")
        if os.path.exists("scraped_posts.json"):
            try:
                with open("scraped_posts.json", "r") as f:
                    count = len(json.load(f))
                st.success(f"✅ `scraped_posts.json`: {count} posts loaded.")
            except:
                st.error("❌ `scraped_posts.json`: Corrupted or empty.")
        else:
            st.warning("🟡 `scraped_posts.json`: Not found. Start by scraping.")

        if os.path.exists("posts_with_replies.json"):
            try:
                with open("posts_with_replies.json", "r") as f:
                    count = len(json.load(f))
                st.success(f"✅ `posts_with_replies.json`: {count} replies generated.")
            except:
                st.error("❌ `posts_with_replies.json`: Corrupted or empty.")
        else:
            st.warning("🟡 `posts_with_replies.json`: Not found. Generate replies next.")

        if os.path.exists("tracked_comments.csv"):
            count = len(load_tracked_comments())
            st.success(f"✅ `tracked_comments.csv`: Tracking {count} comments.")
        else:
            st.warning("🟡 `tracked_comments.csv`: Not found. Post replies to start tracking.")


def page_scrape():
    """Page for scraping a subreddit."""
    st.header("🔍 Scrape a Subreddit")
    with st.form("scrape_form"):
        subreddit_name = st.text_input("Subreddit Name (e.g., onepiece)", "onepiece")
        limit = st.number_input("Number of Posts to Scrape", 1, 50, 5)
        submitted = st.form_submit_button("🚀 Start Scraping", type="primary")

        if submitted and subreddit_name:
            with st.spinner(f"Scraping r/{subreddit_name}..."):
                scrape_subreddit(subreddit_name, limit)
            st.success(f"Scraping complete! Check the status on the Home page.")
            st.balloons()


def page_generate_replies():
    """Page for generating LLM replies."""
    st.header("🤖 Generate LLM Replies")
    if not os.path.exists("scraped_posts.json"):
        st.warning("⚠️ No `scraped_posts.json` file found. Please scrape a subreddit first.")
        return

    try:
        with open("scraped_posts.json", "r") as f:
            posts = json.load(f)
        st.info(f"Found {len(posts)} posts to process.")
        with st.expander("Click to preview first post"):
            st.json(posts[0])
    except Exception as e:
        st.error(f"Could not read scraped posts: {e}")
        return

    if st.button("🧠 Generate Replies Now", type="primary"):
        with st.spinner("Generating replies... This may take a moment."):
            replies = generate_replies_from_file() # This function prints progress to console
        st.success(f"Reply generation complete! {len(replies)} replies saved to `posts_with_replies.json`.")
        st.info("Navigate to 'Review & Post' to see the results.")


def page_review_and_post():
    """Page for reviewing and posting replies with full controls."""
    st.header("✏️ Review & Post Replies")
    posts = load_posts_with_replies() #

    if not posts:
        st.warning("⚠️ No replies found. Please generate replies first on the 'Generate Replies' page.") #
        return

    # Initialize session state if not present
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0
    if 'edited_replies' not in st.session_state:
        st.session_state.edited_replies = {}
    if 'reddit' not in st.session_state:
        st.session_state.reddit = initialize_reddit() #

    if not st.session_state.reddit:
        st.error("Could not connect to Reddit. Check your credentials in `.env` file.") #
        return

    # Check if we are done reviewing
    if st.session_state.review_index >= len(posts):
        st.success("🎉 All posts have been reviewed!") #
        if st.button("Start Over"):
            st.session_state.review_index = 0 #
            st.session_state.edited_replies = {} #
            st.rerun()
        return

    # Display current post for review
    idx = st.session_state.review_index
    post = posts[idx]
    st.progress((idx + 1) / len(posts)) #
    st.caption(f"Reviewing Post {idx + 1} of {len(posts)}") #

    with st.container(border=True):
        st.subheader(post['title'])
        st.markdown(f"**Original Post Text:** *{post['text'] if post['text'] else 'No text content.'}*") #
        st.write(f"**URL:** [{post['url']}]({post['url']})") #

    st.subheader("🤖 Generated Reply")
    reply_key = post['id'] #
    # Load the original reply into the session state if it's not already there
    if reply_key not in st.session_state.edited_replies:
        st.session_state.edited_replies[reply_key] = post['generated_reply'] #

    # The text area for direct editing
    edited_reply = st.text_area(
        "You can directly edit the reply below:",
        st.session_state.edited_replies[reply_key],
        height=150,
        key=f"editor_{reply_key}"
    )
    # Update the session state with any edits made by the user
    st.session_state.edited_replies[reply_key] = edited_reply

    st.markdown("---")
    # Action buttons with accept, reset (edit), and skip (reject)
    col1, col2, col3 = st.columns(3)

    # Column 1: Accept & Post button
    with col1:
        if st.button("✅ Accept & Post", type="primary", use_container_width=True):
            with st.spinner("Posting to Reddit..."):
                comment_id = post_comment_to_reddit(st.session_state.reddit, post['id'], edited_reply) #
            if comment_id:
                save_tracked_comment(comment_id, post['id'], edited_reply) #
                st.success(f"Posted successfully! Comment ID: {comment_id}") #
                st.session_state.review_index += 1 #
                time.sleep(2) 
                st.rerun()

    # Column 2: Reset to Original (the new "Edit") button
    with col2:
        if st.button("🔄 Reset to Original", use_container_width=True):
            # Restore the original AI-generated reply
            st.session_state.edited_replies[reply_key] = post['generated_reply']
            st.rerun()

    # Column 3: Skip / Reject button
    with col3:
        if st.button("⏩ Skip / Reject", use_container_width=True):
            st.session_state.review_index += 1 #
            st.rerun()


def page_performance_dashboard():
    """A live dashboard to view comment performance."""
    st.header("📊 Performance Dashboard")
    st.markdown("This dashboard shows the live performance of comments you've posted.")

    if 'reddit' not in st.session_state:
        st.session_state.reddit = initialize_reddit()
    reddit = st.session_state.reddit

    if 'sentiment_pipeline' not in st.session_state:
        with st.spinner("Loading sentiment analysis model..."):
            st.session_state.sentiment_pipeline = initialize_sentiment_pipeline()
    sentiment_analyzer = st.session_state.sentiment_pipeline

    if not reddit or not sentiment_analyzer:
        st.error("Could not initialize Reddit or Sentiment model. Check console for errors.")
        return

    comment_ids = load_tracked_comments()
    if not comment_ids:
        st.info("No tracked comments found. Post a comment from the 'Review & Post' page first.")
        return

    st.success(f"Found {len(comment_ids)} tracked comments to analyze.")
    for comment_id in reversed(comment_ids): # Show most recent first
        try:
            comment = reddit.comment(id=comment_id)
            comment.refresh() # Get latest score and replies

            with st.expander(f"💬 Comment ID: `{comment.id}` | 👍 Karma: {comment.score}"):
                st.subheader("Your Original Comment:")
                st.info(comment.body)
                st.subheader("Replies Analysis:")

                replies = comment.replies.list()
                if not replies:
                    st.write("No replies yet for this comment.")
                else:
                    for i, reply in enumerate(replies):
                        # Skip replies from the bot itself
                        if reply.author and reply.author.name == reddit.user.me().name:
                            continue

                        st.markdown("---")
                        author = f"/u/{reply.author.name}" if reply.author else "[deleted]"
                        st.write(f"**Reply from {author}:**")
                        st.write(f"> {reply.body}")

                        # Generate and display sentiment heatmap
                        heatmap_filename = f"heatmaps/heatmap_{comment_id}_{reply.id}.png"
                        os.makedirs("heatmaps", exist_ok=True) # Ensure directory exists
                        
                        visualize_reply_sentiment(reply.body, sentiment_analyzer, heatmap_filename)
                        
                        if os.path.exists(heatmap_filename):
                            st.image(heatmap_filename)
                        else:
                            st.warning("Could not generate sentiment heatmap for this reply.")

        except Exception as e:
            st.error(f"Could not fetch data for comment {comment_id}: {e}")

# --- Main App Structure ---

def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Reddit AI Bot Control Panel", page_icon="🤖", layout="wide")

    st.sidebar.title("🛠️ Control Panel")
    page_options = {
        "🏠 Home": page_home,
        "🔍 Scrape Subreddit": page_scrape,
        "🤖 Generate Replies": page_generate_replies,
        "✏️ Review & Post": page_review_and_post,
        "📊 Performance Dashboard": page_performance_dashboard,
    }

    page_selection = st.sidebar.radio("Navigation", list(page_options.keys()))
    st.sidebar.markdown("---")
    st.sidebar.info("This app automates scraping, replying, and analyzing Reddit engagement.")

    # Call the selected page's function
    page_options[page_selection]()

if __name__ == "__main__":
    main()