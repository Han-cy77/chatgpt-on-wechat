# Web Channel Documentation

This document describes the Web Channel features, API endpoints, and usage instructions for the ChatGPT-on-WeChat project.

## Features

- **Web Interface**: A clean, responsive chat interface similar to ChatGPT.
- **User Authentication**: Secure login and registration system.
- **Conversation History**: 
  - Persistent storage of chat history.
  - List view with pagination.
  - Search by keyword.
  - Filter by date range.
  - Delete conversations.
- **Session Management**: 7-day session timeout with secure token-based authentication.

## User Manual

### 1. Accessing the Web Interface
1. Ensure `channel_type` is set to `"web"` in `config.json`.
2. Start the application: `python app.py`.
3. Open your browser and navigate to `http://localhost:9899/chat`.

### 2. Authentication
- **Register**: Click "Login" -> "No account? Go to Register". Enter a username and password.
- **Login**: Enter your credentials to access your personal history.
- **Logout**: Click your username in the sidebar -> "Logout".

### 3. Managing Conversations
- **New Chat**: Click the "+ New Chat" button.
- **View History**: Your past conversations are listed in the sidebar. Click one to load it.
- **Search**: Enter keywords in the search box to find specific conversations.
- **Filter by Date**: Select a start and/or end date to filter conversations by their last update time.
- **Delete**: Hover over a conversation in the sidebar and click the trash icon.
- **Pagination**: Scroll to the bottom of the sidebar and click "Load More" if there are more conversations.

## API Documentation

### Authentication

#### POST /register
Register a new user.
- **Body**: `{"username": "...", "password": "..."}`
- **Response**: `{"status": "success"}` or `{"status": "error", "message": "..."}`

#### POST /login
Login and receive an authentication token.
- **Body**: `{"username": "...", "password": "..."}`
- **Response**: `{"status": "success", "token": "uuid-token", "username": "..."}`

### Conversations

#### GET /conversations
List conversations with filtering and pagination.
- **Headers**: `Authorization: Bearer <token>` or Query Param `token=<token>`
- **Query Params**:
  - `limit`: Number of items per page (default: 20).
  - `offset`: Offset for pagination (default: 0).
  - `keyword`: Search term for title filtering.
  - `start_date`: Timestamp (seconds) for start of date range.
  - `end_date`: Timestamp (seconds) for end of date range.
- **Response**:
  ```json
  {
    "status": "success",
    "data": [
      {"id": "...", "title": "...", "updated_at": 1234567890},
      ...
    ],
    "pagination": {
      "total": 100,
      "limit": 20,
      "offset": 0
    }
  }
  ```

#### GET /conversations?id=<id>
Get details of a specific conversation.
- **Query Params**: `id=<conversation_id>`
- **Response**: `{"status": "success", "data": {"id": "...", "messages": [...]}}`

#### DELETE /conversations
Delete a conversation.
- **Query Params**: `id=<conversation_id>`
- **Response**: `{"status": "success"}`

### Messaging

#### POST /message
Send a message to the bot.
- **Body**:
  ```json
  {
    "session_id": "...",
    "message": "Hello",
    "token": "..." (optional, for history saving),
    "conversation_id": "..." (optional, to append to existing chat)
  }
  ```
- **Response**: `{"status": "success", "request_id": "...", "conversation_id": "..."}`

## Deployment & Security

### HTTPS Configuration
For production environments, it is **strongly recommended** to use a reverse proxy (like Nginx or Apache) to enable HTTPS. This ensures that passwords and tokens are encrypted during transmission.

**Nginx Example Configuration:**
```nginx
server {
    listen 443 ssl;
    server_name chat.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:9899;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database
- Data is stored in `channel/web/web_chat.db` (SQLite).
- Passwords are salted and hashed using SHA-256.
- Sessions expire automatically after 7 days.
