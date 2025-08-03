import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_replies_from_file(filename="scraped_posts.json"):
    """Loads scraped posts and generates a reply for each using an LLM."""
    
    # --- Step 1: Configure the LLM with the environment variable ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not found.")
        print("Please add GEMINI_API_KEY to your .env file")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")
        return

    # --- Step 2: Load the scraped posts ---
    try:
        with open(filename, "r", encoding="utf-8") as f:
            posts = json.load(f)
        print(f"📂 Loaded {len(posts)} posts from {filename}")
    except FileNotFoundError:
        print(f"❌ Error: The file '{filename}' was not found. Please run scraper.py first.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in {filename}")
        return

    # --- Step 3: Generate a reply for each post ---
    generated_replies = []
    
    for i, post in enumerate(posts, 1):
        print("\n" + "=" * 60)
        print(f"📝 Processing post {i}/{len(posts)}: \"{post['title'][:50]}{'...' if len(post['title']) > 50 else ''}\"")
        
        # Improved prompt with better structure and clarity
        prompt = f"""You are a passionate One Piece fan who's witty, respectful, and knowledgeable. You respond with dignity and humor while staying authentic to your personality.

**POST DETAILS:**
Title: {post['title']}
Content: {post['text'] if post['text'].strip() else '[No text content - check URL/image for context]'}
URL: {post['url']}
Upvotes: {post['score']}

**RESPONSE GUIDELINES:**
- Maximum 40 words
- Be humorous and insightful
- Show One Piece knowledge when relevant
- Stay respectful but don't be afraid to give honest opinions
- Sound natural and human, avoid generic responses
- If post is question-based, provide helpful insight
- If post is humorous, match the energy appropriately

**Your Reply:**"""

        try:
            response = model.generate_content(prompt)
            reply_text = response.text.strip()
            
            print("🤖 Generated Reply:")
            print(f"   \"{reply_text}\"")
            print(f"📊 Word count: {len(reply_text.split())} words")
            
            # Store the reply with post data
            post_with_reply = post.copy()
            post_with_reply['generated_reply'] = reply_text
            post_with_reply['word_count'] = len(reply_text.split())
            generated_replies.append(post_with_reply)
            
        except Exception as e:
            print(f"❌ Could not generate reply for post ID {post['id']}: {e}")
            continue

    # --- Step 4: Save replies to a new file ---
    if generated_replies:
        output_filename = "posts_with_replies.json"
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(generated_replies, f, indent=4, ensure_ascii=False)
            print(f"\n✅ Successfully saved {len(generated_replies)} posts with replies to {output_filename}")
        except Exception as e:
            print(f"❌ Error saving replies: {e}")
    
    print("\n🎉 Reply generation completed!")
    return generated_replies


def preview_replies(filename="posts_with_replies.json"):
    """Preview generated replies in a clean format."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            posts_with_replies = json.load(f)
        
        print("📋 GENERATED REPLIES PREVIEW")
        print("=" * 80)
        
        for i, post in enumerate(posts_with_replies, 1):
            print(f"\n{i}. 📝 {post['title']}")
            print(f"   🤖 Reply: \"{post['generated_reply']}\"")
            print(f"   📊 {post['word_count']} words")
            
    except FileNotFoundError:
        print(f"❌ No replies file found. Run generate_replies_from_file() first.")
    except Exception as e:
        print(f"❌ Error reading replies: {e}")


if __name__ == "__main__":
    # Generate replies for scraped posts
    generate_replies_from_file()
