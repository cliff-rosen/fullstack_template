COGNIFY

# Cognify – Your Intelligent Knowledge Organizer

## Overview

Cognify helps you organize and enrich your personal and professional knowledge through a structured, searchable repository. The system provides a three-panel interface with quick entry capabilities for efficient knowledge management.

## Target Users

Ideal for professionals, creators, and knowledge workers who need a seamless way to organize, track, and develop their ideas over time. Whether brainstorming, managing projects, or reflecting on personal goals, Cognify adapts to your process.

## Feature Matrix

| Feature | MVP Status | Description |
|---------|------------|-------------|
| Quick Entry | ✅ MVP | Global entry with topic selection/creation |
| Entry Management | ✅ MVP | Create, view, and organize entries |
| Topic Management | ✅ MVP | Manual topic creation and organization |
| User Authentication | ✅ MVP | Email/password based login |
| Chat Interface | ✅ MVP | Basic contextual chat within topics |
| Automatic Categorization | 🔄 Future | AI-driven topic detection and organization |
| Rich Text & Attachments | 🔄 Future | Enhanced entry formatting and file support |
| Advanced Chat | 🔄 Future | Threading, multiple conversations |
| Collaboration | 🔄 Future | Multi-user support and sharing |

## Technical Architecture

### Frontend Stack
- React with TypeScript
- Tailwind CSS
- shadcn/ui components

### Backend Stack
- RESTful API
- MariaDB
- JWT Authentication

## User Interface

### Layout Structure
```
┌─────────────────────────────────────────────────────┐
│                  Quick Entry Area                    │
│ ┌─────────┐ ┌────────────────────┐ ┌─────────────┐ │
│ │  Entry  │ │ Topic ▼            │ │    Send     │ │
│ └─────────┘ └────────────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────┘
┌─────────────┬────────────────┬─────────────┐
│  Topics     │    Entries     │    Chat     │
│  (Left)     │   (Center)     │   (Right)   │
├─────────────┼────────────────┼─────────────┤
│ • List      │ • Entry List   │ • Messages  │
│ • Add New   │ • Sort Options │ • Input     │
│ • Select    │ • Topic Entry  │ • History   │
└─────────────┴────────────────┴─────────────┘
```

### Interface Components

#### Quick Entry Area
- Message input field: Primary text entry area
- Topic selector dropdown:
  - List of existing topics
  - "NEW TOPIC" option at top
  - Optional selection (can leave blank)
- Send button: Creates entry and optionally new topic

#### Left Panel (Topics)
- Topics list with add/edit/delete options
- Overview section for unassigned entries
- Quick-add buttons for new topics

#### Center Panel (Entries)
- Chronological entry list
- Sort and filter options
- Topic-specific entry field

#### Right Panel (Chat)
- Topic-specific chat interface
- Message history
- Input field for new messages

## Database Schema

### Users
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);
```

### Topics
```sql
CREATE TABLE topics (
    topic_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_topics (user_id, topic_name)
);
```

### Entries
```sql
CREATE TABLE entries (
    entry_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    topic_id INT,
    content TEXT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    INDEX idx_user_entries (user_id, creation_date)
);
```

### Chat Messages
```sql
CREATE TABLE chat_messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    topic_id INT,
    user_id INT,
    message_text TEXT NOT NULL,
    message_type ENUM('user', 'assistant', 'system') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_topic_messages (topic_id, timestamp)
);
```

## API Endpoints

### Authentication
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
```

### Topics
```
GET    /api/topics
POST   /api/topics
PUT    /api/topics/:topicId
DELETE /api/topics/:topicId
```

### Entries
```
GET    /api/entries
GET    /api/entries/topic/:topicId
POST   /api/entries
PUT    /api/entries/:topicId
DELETE /api/entries/:topicId
```

### Chat
```
GET    /api/chat/topic/:topicId
POST   /api/chat/topic/:topicId
DELETE /api/chat/topic/:topicId/message/:messageId
```

## User Flows

### Quick Entry Flow
1. User enters text in quick entry field
2. User can either:
   - Select existing topic from dropdown
   - Choose "NEW TOPIC" and enter new topic name
   - Leave topic unselected (entry goes to "Overview")
3. Click Send or press Enter to create entry
4. If "NEW TOPIC" selected:
   - Modal prompts for new topic name
   - Creates topic and assigns entry
   - Adds topic to sidebar list
5. Entry appears in:
   - Selected topic's entry list
   - Overview if no topic selected
   - Newly created topic if "NEW TOPIC" used

### Topic Management Flow
1. Create new topic via:
   - Sidebar "+" button
   - During entry creation
   - Quick entry "NEW TOPIC" option
2. Select topic to view associated entries
3. Edit topic name via sidebar context menu
4. Delete topic (requires confirmation)

### Entry Management Flow
1. Create entries through:
   - Quick entry area
   - Topic-specific entry field
   - Topic quick-add button
2. View entries:
   - Chronologically within topics
   - In Overview if unassigned
3. Sort entries by date (ascending/descending)

### Chat Interaction Flow
1. Each topic has dedicated chat thread
2. Messages are typed and sent via input field
3. Messages show sender and timestamp
4. Overview chat available for general assistance

## Error Handling

### API Responses
- 200: Success
- 400: Invalid request
- 401: Unauthorized
- 404: Resource not found
- 500: Server error

### User Feedback
- Toast notifications for actions
- Inline validation for forms
- Loading states for async operations
- Error messages for failed operations

## Future Enhancements

### Intelligence Features
- Automatic topic suggestion
- Content categorization
- Trend detection
- Topic summaries

### Enhanced Entry Features
- Rich text formatting
- File attachments
- Tags and labels
- Cross-entry linking

### Advanced Chat
- Multiple conversations per topic
- Message threading
- Chat history search
- Context-aware responses

### Collaboration
- Multi-user accounts
- Sharing and permissions
- Comments on entries
- Real-time updates

