# Knowledge Graph Social Network System

A synthetic knowledge graph-based social network system inspired by TikTok, leveraging deep graph reasoning for content recommendation and user engagement.

## Features

- **User Management**: Registration, authentication, and profile management
- **Content Creation**: Upload, edit, and share short videos
- **Knowledge Graph**: Represents relationships between users, content, hashtags, and interests
- **Recommendation Engine**: Personalized content recommendations based on user behavior and graph analysis
- **Social Interactions**: Like, comment, share, and follow functionality
- **Trending Content**: Discover popular content based on engagement metrics
- **Analytics**: Track content performance and user engagement
- **AI-Generated Content**: Content created by AI agents tailored to user preferences

## Architecture

The system is built using a microservices architecture with the following components:

- **API Layer**: FastAPI-based RESTful API endpoints
- **Service Layer**: Business logic and service orchestration
- **Data Layer**: Graph database and relational database integration
- **ML Models**: Recommendation algorithms and content analysis
- **AI Agents**: Specialized content generation agents
- **Utils**: Helper functions and utilities

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration

### Running the Application

```
python src/main.py
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### Initializing Sample Data

To populate the system with sample data for testing:

```
python src/scripts/init_db.py
```

This will create sample users, content, and interactions.

## API Endpoints

The system provides the following API endpoints:

### User API (`/api/users`)

- `POST /register` - Register a new user
- `POST /token` - Authenticate and get access token
- `GET /me` - Get current user information
- `PUT /me` - Update current user information
- `POST /me/profile-picture` - Upload profile picture
- `GET /{user_id}` - Get user by ID
- `GET /{user_id}/followers` - Get user's followers
- `GET /{user_id}/following` - Get users followed by user
- `POST /{user_id}/follow` - Follow a user
- `POST /{user_id}/unfollow` - Unfollow a user
- `GET /search` - Search for users

### Content API (`/api/content`)

- `POST /` - Create new content
- `GET /{content_id}` - Get content by ID
- `GET /{content_id}/video` - Get content video file
- `GET /{content_id}/thumbnail` - Get content thumbnail
- `PUT /{content_id}` - Update content
- `DELETE /{content_id}` - Delete content
- `POST /{content_id}/view` - Record content view
- `POST /{content_id}/like` - Like content
- `POST /{content_id}/share` - Share content
- `POST /{content_id}/comments` - Add comment to content
- `GET /{content_id}/comments` - Get content comments
- `GET /comments/{comment_id}/replies` - Get comment replies
- `POST /comments/{comment_id}/like` - Like a comment
- `GET /user/{user_id}` - Get user's content
- `GET /search` - Search for content
- `GET /hashtag/{hashtag}` - Get content by hashtag
- `GET /trending/hashtags` - Get trending hashtags

### Social API (`/api/social`)

- `GET /feed` - Get social feed from followed users
- `GET /explore` - Get explore page content
- `GET /notifications` - Get user notifications
- `GET /activity` - Get user activity
- `GET /graph-visualization` - Get graph visualization data

### Recommendations API (`/api/recommendations`)

- `POST /feed` - Get personalized content feed
- `GET /trending` - Get trending content
- `GET /similar-content/{content_id}` - Get similar content
- `GET /similar-users/{user_id}` - Get similar users
- `POST /update-interests` - Update user interests

### AI Content API (`/api/ai-content`)

- `GET /agents` - Get list of AI content generation agents
- `GET /agents/{agent_id}` - Get AI agent by ID
- `POST /agents` - Create a new AI agent
- `PUT /agents/{agent_id}` - Update an AI agent
- `DELETE /agents/{agent_id}` - Delete an AI agent
- `GET /preferences/{user_id}` - Get user preferences for AI content
- `PUT /preferences/{user_id}` - Update user preferences for AI content
- `POST /generate` - Generate AI content based on user preferences
- `POST /feed` - Get personalized AI content feed for a user
- `POST /interaction/{user_id}/{content_id}` - Record user interaction with AI content
- `GET /analysis/{user_id}` - Analyze user preferences based on interaction history

### Analytics API (`/api/analytics`)

- `GET /content/{content_id}/metrics` - Get content metrics
- `GET /user/{user_id}/metrics` - Get user metrics
- `GET /trending/topics` - Get trending topics
- `GET /dashboard` - Get analytics dashboard

## AI-Generated Content

The system includes a feature for AI-generated content, where specialized AI agents create content tailored to user preferences. Initially, content is generated randomly, but as users interact with the system, the AI agents learn their preferences and generate more targeted content.

### AI Agents

The system includes several default AI agents, each specializing in different content types:

- **TravelAgent**: Creates travel and adventure content
- **FoodieBot**: Creates food and cooking content
- **TechGuru**: Creates technology and gadget content
- **FitnessCoach**: Creates fitness and wellness content
- **FashionDesigner**: Creates fashion and style content

### User Preference Learning

The system tracks user interactions with content (views, likes, comments, shares) and analyzes these interactions to determine user preferences. These preferences are then used to:

1. Select appropriate AI agents for content generation
2. Choose relevant topics and themes for the content
3. Tailor the content format to user preferences

### Integration with Recommendations

AI-generated content is seamlessly integrated into the recommendation engine, appearing alongside regular user-generated content in feeds. The system allows controlling the ratio of AI to user-generated content through the recommendation API.

## Development

### Project Structure

```
├── src/
│   ├── api/           # API endpoints
│   │   ├── users.py
│   │   ├── content.py
│   │   ├── social.py
│   │   ├── recommendations.py
│   │   ├── ai_content.py
│   │   └── analytics.py
│   ├── models/        # Data models and schemas
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── content.py
│   │   ├── social.py
│   │   └── recommendation.py
│   ├── services/      # Business logic
│   │   ├── knowledge_graph.py
│   │   ├── user.py
│   │   ├── content.py
│   │   ├── ai_content.py
│   │   └── recommendation.py
│   ├── scripts/       # Utility scripts
│   │   └── init_db.py
│   ├── utils/         # Helper functions
│   ├── data/          # Data storage
│   └── main.py        # Application entry point
├── tests/             # Test cases
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

## License

MIT 