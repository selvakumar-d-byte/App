# LevelUpHive - Project Structure

## Overview
LevelUpHive is a course learning platform built with FastAPI, React, and MongoDB. Users can browse courses, watch videos sequentially, track progress, and earn certificates.

## Folder Structure

```
/app/
├── backend/
│   ├── server.py           # FastAPI backend with all API endpoints
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main app component with routing & auth context
│   │   ├── App.css        # Global styles
│   │   ├── pages/
│   │   │   ├── HomePage.js           # Landing page
│   │   │   ├── CoursesPage.js        # Course listing with filters
│   │   │   └── CourseDetailPage.js   # Course videos & player
│   │   └── components/
│   │       ├── Header.js             # Navigation header
│   │       ├── AuthModal.js          # Login/signup modal
│   │       ├── VideoPlayer.js        # Video player with restrictions
│   │       ├── CertificateModal.js   # Certificate display & download
│   │       └── ui/                   # Shadcn UI components
│   ├── package.json
│   └── .env              # Frontend environment variables
│
└── scripts/
    └── seed_data.py      # Database seeding script (8 courses, 24 videos)
```

## Key Features

### 1. Authentication
- Signup/Login via modal popup
- JWT-based authentication
- Password hashing with bcrypt
- Token stored in localStorage

### 2. Course Management
- Browse courses in grid layout (4 per row)
- Search courses by name
- Filter by language (Tamil/English)
- Clear filters button

### 3. Video Learning
- Sequential video watching (must complete videos in order)
- First video always unlocked
- Progress tracking per video
- Cannot skip ahead using video controls or keyboard
- Can only forward up to previously watched position
- Completed videos marked with checkmark
- Completed videos can be replayed without restrictions

### 4. Certificate System
- Automatically generated after completing all course videos
- Professional certificate design
- Displays user name and course name
- Download/print functionality

### 5. Progress Persistence
- User progress saved in MongoDB
- Progress persists across sessions
- Resume from last watched position

## Database Collections

### users
- id, name, email, password (hashed), created_at

### courses
- id, name, description, language, image_url, created_at

### videos
- id, course_id, title, video_url, duration, order

### progress
- id, user_id, course_id, video_id, watched_duration, completed, last_watched

### certificates
- id, user_id, course_id, user_name, course_name, issued_at

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Courses
- GET /api/courses (with search & language params)
- GET /api/courses/{id}
- GET /api/courses/{id}/videos

### Progress
- POST /api/progress/update
- GET /api/progress/user/{user_id}/course/{course_id}

### Certificates
- POST /api/certificates/generate
- GET /api/certificates/user/{user_id}/course/{course_id}

## Environment Variables

### Backend (.env)
- MONGO_URL (MongoDB connection)
- DB_NAME (Database name)
- CORS_ORIGINS (CORS settings)
- SECRET_KEY (JWT secret)

### Frontend (.env)
- REACT_APP_BACKEND_URL (Backend API URL)

## Running the Application

Backend: Managed by supervisor (auto-restart enabled)
Frontend: Managed by supervisor (auto-restart enabled)

To restart services:
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## Sample Data
Run `/app/scripts/seed_data.py` to populate the database with:
- 8 courses (4 English, 4 Tamil)
- 24 videos (3 per course)
- Sample video URLs from public domain

## Design Theme
- Navy/dark blue background gradient
- Cyan accent color for buttons and highlights
- Space Grotesk font for headings
- Inter font for body text
- Glass-morphism effects for cards
- Responsive grid layout
