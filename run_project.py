# run_project.py

# Import the core functions from your other project files
from scraper import scrape_subreddit
from llm_handler import generate_replies_from_file
from main import review_and_post_workflow
from analysis import analyze_comment_performance, initialize_reddit, initialize_sentiment_pipeline
import csv
import subprocess
import sys

def show_menu():
    """Displays the main menu to the user."""
    print("\n" + "="*40)
    print("🤖 Reddit AI Bot Control Panel 🤖")
    print("="*40)
    print("1. Scrape a Subreddit")
    print("2. Generate LLM Replies for Scraped Posts")
    print("3. Review, Edit, and Post Replies")
    print("4. Analyze Performance of Posted Comments")
    print("5. Run Full Workflow (1 -> 2 -> 3)")
    print("6. Launch Streamlit Web Interface")
    print("7. Exit")
    print("-"*40)

def main():
    """The main driver function to run the project."""
    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            # Scrape a subreddit
            subreddit_name = input("Enter the name of the subreddit to scrape (e.g., onepiece): ")
            if not subreddit_name:
                subreddit_name = "onepiece" # Default value
            scrape_subreddit(subreddit_name)

        elif choice == '2':
            # Generate LLM replies
            print("\n--- Starting LLM Reply Generation ---")
            generate_replies_from_file("scraped_posts.json")

        elif choice == '3':
            # Review and post replies
            print("\n--- Starting Interactive Review Workflow ---")
            review_and_post_workflow("posts_with_replies.json")

        elif choice == '4':
            # Analyze performance
            print("\n--- Starting Performance Analysis ---")
            reddit_instance = initialize_reddit()
            sentiment_pipeline = initialize_sentiment_pipeline()
            if reddit_instance and sentiment_pipeline:
                try:
                    with open('tracked_comments.csv', 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader) # Skip header
                        for row in reader:
                            if row:
                                analyze_comment_performance(reddit_instance, sentiment_pipeline, row[0])
                except FileNotFoundError:
                    print("❌ 'tracked_comments.csv' not found. Post a comment first.")
            print("\n🎉 Analysis complete!")

        elif choice == '5':
            # Run the full end-to-end workflow
            print("\n--- Running Full Workflow ---")
            # Step 1
            subreddit_name = input("Enter the name of the subreddit to scrape (e.g., onepiece): ")
            if not subreddit_name:
                subreddit_name = "onepiece"
            scrape_subreddit(subreddit_name)
            # Step 2
            print("\n--- Starting LLM Reply Generation ---")
            generate_replies_from_file("scraped_posts.json")
            # Step 3
            print("\n--- Starting Interactive Review Workflow ---")
            review_and_post_workflow("posts_with_replies.json")

        elif choice == '6':
            # Launch Streamlit web interface
            print("\n🌐 Launching Streamlit Web Interface...")
            print("Opening in your default browser...")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
            except Exception as e:
                print(f"❌ Error launching Streamlit: {e}")
                print("💡 Try running manually: streamlit run streamlit_app.py")

        elif choice == '7':
            # Exit the program
            print("👋 Exiting the control panel. Goodbye!")
            break

        else:
            print("⚠️ Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
