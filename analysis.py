# analysis.py

import os
import csv
import praw
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

def initialize_reddit():
    """Initializes and returns an authenticated PRAW instance."""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
        print(f"✅ Authenticated as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print(f"❌ Reddit authentication failed: {e}")
        return None

def initialize_sentiment_pipeline():
    """Initializes the advanced Hugging Face pipeline trained on social media."""
    try:
        model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        sentiment_analyzer = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
        print("✅ Sentiment model loaded")
        return sentiment_analyzer
    except Exception as e:
        print(f"❌ Sentiment model failed: {e}")
        return None

def get_composite_score(results):
    """
    Calculates a single score from the model's output.
    The score ranges from -1 (very negative) to +1 (very positive).
    """
    try:
        if isinstance(results, list) and len(results) > 0:
            if isinstance(results[0], dict):
                result = results[0]
                label = result['label'].upper()
                score = result['score']
                
                if 'POSITIVE' in label:
                    return score
                elif 'NEGATIVE' in label:
                    return -score
                else:
                    return 0.0
            else:
                return get_composite_score(results[0])
        elif isinstance(results, dict):
            label = results['label'].upper()
            score = results['score']
            
            if 'POSITIVE' in label:
                return score
            elif 'NEGATIVE' in label:
                return -score
            else:
                return 0.0
        else:
            return 0.0
            
    except Exception:
        return 0.0

def visualize_reply_sentiment(reply_text, sentiment_analyzer, filename="sentiment_heatmap.png"):
    """Creates and saves a heatmap visualizing word-level sentiment contribution."""
    words = reply_text.split()
    if not words: 
        return None

    try:
        base_results = sentiment_analyzer(reply_text)
        base_score = get_composite_score(base_results)
        word_importance_scores = []
        for i in range(len(words)):
            temp_text = ' '.join(words[:i] + words[i+1:])
            if not temp_text.strip(): 
                word_importance_scores.append(0.0)
                continue
            
            temp_results = sentiment_analyzer(temp_text)
            temp_score = get_composite_score(temp_results)
            importance = base_score - temp_score
            word_importance_scores.append(importance)

        if not word_importance_scores: 
            return base_score
        
        plt.figure(figsize=(max(len(words) * 0.9, 8), 2.5))
        scores_to_plot = np.array(word_importance_scores).reshape(1, -1)
        
        sns.heatmap(
            scores_to_plot, annot=np.array(words).reshape(1, -1), fmt='',
            cmap="coolwarm", linewidths=.5, cbar=True,
            cbar_kws={'label': 'Sentiment Impact'}, xticklabels=False,
            yticklabels=False, annot_kws={"size": 10}
        )
        
        plt.title("Sentiment Analysis", fontsize=12)
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        return base_score
        
    except Exception:
        return None

def get_sentiment_emoji(score):
    """Returns an emoji representation of the sentiment score."""
    if score > 0.6: return "😄"
    elif score > 0.2: return "🙂"
    elif score > -0.2: return "😐"
    elif score > -0.6: return "😠"
    else: return "😡"

def analyze_comment_performance(reddit, sentiment_analyzer, comment_id):
    """Analyzes a single comment for its karma and the sentiment of its replies."""
    try:
        comment = reddit.comment(id=comment_id)
        comment.refresh()
        
        karma = comment.score
        replies = comment.replies.list()
        
        print(f"\n📊 Comment {comment_id} | Karma: {karma} | Replies: {len(replies)}")
        
        if not replies:
            return

        for i, reply in enumerate(replies):
            if reply.author and reply.author.name == reddit.user.me().name:
                continue

            reply_text = reply.body[:512]
            heatmap_filename = f"heatmap_{comment_id}_reply_{i+1}.png"
            overall_score = visualize_reply_sentiment(reply_text, sentiment_analyzer, heatmap_filename)
            
            if overall_score is not None:
                emoji = get_sentiment_emoji(overall_score)
                print(f"   Reply {i+1}: {overall_score:.2f} {emoji}")

    except Exception as e:
        print(f"❌ Error analyzing {comment_id}: {e}")

if __name__ == "__main__":
    reddit_instance = initialize_reddit()
    sentiment_pipeline = initialize_sentiment_pipeline()

    if not reddit_instance or not sentiment_pipeline:
        exit(1)
        
    tracking_file = 'tracked_comments.csv'
    try:
        with open(tracking_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            comment_count = 0
            
            for row in reader:
                if not row: continue
                comment_id = row[0]
                analyze_comment_performance(reddit_instance, sentiment_pipeline, comment_id)
                comment_count += 1
                
            print(f"\n✅ Analyzed {comment_count} comments")
            
    except FileNotFoundError:
        print(f"❌ '{tracking_file}' not found. Run main.py first.")
    except Exception as e:
        print(f"❌ Error: {e}")