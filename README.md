# Reddit Bot 🏴‍☠️

An intelligent Reddit bot that scrapes One Piece subreddit posts, generates contextual replies using AI, and provides comprehensive analytics with sentiment analysis.

## Features

- **Automated Post Scraping**: Fetches latest posts from r/onepiece
- **AI-Powered Replies**: Generates witty, knowledgeable One Piece fan responses using Google's Gemini AI
- **Interactive Review System**: Manual review and editing of AI-generated replies before posting
- **Sentiment Analysis**: Advanced sentiment analysis of replies using RoBERTa model
- **Visual Analytics**: Word-level sentiment heatmaps for each reply
- **Live Dashboard**: Real-time Streamlit dashboard for monitoring bot performance
- **Performance Tracking**: Karma tracking and engagement metrics

## Project Structure

```
Project/
├── scraper.py          # Reddit post scraping
├── llm_handler.py      # AI reply generation
├── main.py            # Review workflow and posting
├── analysis.py        # Sentiment analysis and heatmaps
├── dashboard.py       # Streamlit dashboard
├── .env              # API credentials (not included)
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Project
```

### 2. Create Virtual Environment
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file with your API credentials:

```env
# Reddit API Credentials
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
USER_AGENT=python:reddit_onepiece_bot:1.0 by /u/yourusername
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key
```

**Getting Reddit API Credentials:**
1. Go to https://www.reddit.com/prefs/apps/
2. Create a new app (choose "script" type)
3. Note down your client ID and secret

**Getting Gemini API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key

## Usage

### 1. Scrape Posts
```bash
python3 scraper.py
```
Fetches latest posts from r/onepiece and saves to `scraped_posts.json`

### 2. Generate AI Replies
```bash
python3 llm_handler.py
```
Creates contextual replies for each post using Gemini AI

### 3. Review and Post
```bash
python3 main.py
```
Interactive workflow to review, edit, and post replies to Reddit

### 4. Analyze Performance
```bash
python3 analysis.py
```
Generates sentiment analysis and heatmaps for posted comments

### 5. Launch Dashboard
```bash
streamlit run dashboard.py
```
Real-time dashboard showing bot performance and analytics

## Results

### Sample Bot Performance

#### Comment Analytics
```
📊 Comment n6nyyv7 | Karma: 5 | Replies: 3
   Reply 1: 0.67 😄
   Reply 2: -0.23 😠
   Reply 3: 0.45 🙂

📊 Comment n6nz2qz | Karma: 8 | Replies: 1
   Reply 1: 0.78 😄
```

#### AI-Generated Reply Examples

**Post:** "Who's stronger: Zoro or Sanji?"
**AI Reply:** "Classic debate! Zoro's got the swords and dedication, but Sanji's speed and tactics are insane. Both would protect the crew with their lives though! 💪"
**Performance:** 12 upvotes, 4 positive replies

**Post:** "Just finished Marineford arc..."
**AI Reply:** "The emotional rollercoaster hits different! Ace's sacrifice still gives me chills. Luffy's growth after that tragedy was incredible to witness. 😭"
**Performance:** 18 upvotes, 2 positive replies

### Dashboard Screenshots

![Dashboard Overview](dashboard_screenshot.png)
*Real-time monitoring of bot performance with karma tracking*

![Sentiment Heatmap](heatmap_example.png)
*Word-level sentiment analysis showing which words trigger positive/negative responses*

## Technical Features

### AI Reply Generation
- **Model**: Google Gemini 1.5 Flash
- **Max Length**: 40 words per reply
- **Personality**: Witty, respectful One Piece enthusiast
- **Context Awareness**: Considers post content, title, and URL

### Sentiment Analysis
- **Model**: Cardiff NLP RoBERTa (Twitter-trained)
- **Granularity**: Word-level importance scoring
- **Visualization**: Color-coded heatmaps
- **Metrics**: Composite sentiment scores (-1 to +1)

### Performance Tracking
- **Karma Monitoring**: Real-time upvote/downvote tracking
- **Reply Analysis**: Sentiment of community responses
- **Engagement Metrics**: Reply count and interaction quality
- **Historical Data**: CSV-based comment tracking

## File Outputs

- `scraped_posts.json`: Raw scraped post data
- `posts_with_replies.json`: Posts with AI-generated replies
- `tracked_comments.csv`: Posted comment IDs and timestamps
- `heatmap_*.png`: Sentiment analysis visualizations

## Safety Features

- **Manual Review**: All replies reviewed before posting
- **Edit Capability**: Modify AI replies before posting
- **Rate Limiting**: Prevents spam posting
- **Error Handling**: Graceful failure recovery
- **Respect Rules**: Follows Reddit API guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect Reddit's API terms of service and community guidelines.

## Disclaimer

This bot is designed to engage positively with the One Piece community. Always follow subreddit rules and Reddit's content policy. The bot should enhance discussion, not spam or manipulate conversations.

---

Built with ❤️ for the One Piece community by a passionate nakama! 🏴‍☠️
