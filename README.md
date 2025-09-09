# Ehron Memory Album

A Django-powered memory album application that grows with your child, unlocking new features based on their age.

## Features

### Core Features
- **Timeline-based Memory Album**: Upload photos, videos, audio recordings, and text memories
- **Age-based Feature Unlocking**: New features unlock as your child grows
- **Role-based Access**: Owner, Family Members, and Child roles with appropriate permissions
- **Responsive Design**: Beautiful Tailwind CSS interface that works on all devices

### Age-Based Features
- **Year 0-1**: Basic memories, milestones, growth chart, AI captions
- **Year 2+**: Memory map with geotagged photos
- **Year 3+**: AI-powered bedtime story generator
- **Year 5+**: Voice notes and drawings
- **Year 13+**: Guestbook and journaling
- **Year 18+**: Full export and ownership transfer

### AI-Powered Features
- Photo caption generation using OpenAI
- Personalized bedtime story creation
- Audio transcription (Whisper integration ready)
- Year-in-review video generation

## Technology Stack

- **Backend**: Django 5.0, PostgreSQL
- **Frontend**: Tailwind CSS, HTMX for dynamic interactions
- **File Storage**: Local storage (development) / AWS S3 (production)
- **AI Integration**: OpenAI GPT for captions and stories
- **Task Queue**: Celery with Redis
- **Deployment Ready**: Gunicorn, production settings

## Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ehron-memory-album
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Load Initial Data** (Optional)
   ```bash
   python manage.py loaddata fixtures/milestones.json
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery Worker** (for AI features)
   ```bash
   celery -A ehron worker -l info
   ```

## Configuration

### Required Environment Variables
- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `OPENAI_API_KEY`: For AI features (optional but recommended)
- `CELERY_BROKER_URL`: Redis URL for task queue

### Optional Features
- **AWS S3**: Set `USE_S3=True` and configure AWS credentials
- **Email**: Configure SMTP settings for invitations

## Usage

1. **Create Account**: Register as the album owner and add your child's information
2. **Invite Family**: Send invitations to family members to join the album
3. **Add Memories**: Upload photos, videos, and create text memories
4. **Track Milestones**: Record important developmental milestones
5. **Create Albums**: Organize memories into themed collections
6. **AI Features**: Generate captions and bedtime stories (requires OpenAI API key)

## Project Structure

```
ehron/
├── accounts/          # User authentication and child management
├── memories/          # Core memory functionality
├── milestones/        # Milestone tracking and growth charts
├── albums/            # Memory organization into albums
├── ai_features/       # AI-powered features (stories, captions)
├── core/              # Dashboard, settings, and app-wide features
├── templates/         # HTML templates
├── static/           # CSS, JavaScript, images
└── media/            # User uploads (development)
```

## Security Features

- Role-based access control
- Private family albums with invitation-only access
- Secure file uploads with validation
- CSRF protection and secure headers
- Age-appropriate feature gating

## Production Deployment

The application is configured for production deployment with:
- Gunicorn WSGI server
- PostgreSQL database
- AWS S3 for file storage
- Redis for caching and task queue
- Comprehensive logging
- Security middleware

## Contributing

This is a personal family project, but if you'd like to adapt it for your own use:
1. Fork the repository
2. Customize the child information and branding
3. Add your own AI features or integrations
4. Deploy to your preferred hosting platform

## License

This project is created for personal use. Please respect privacy and family-oriented nature of the application.

---

Built with ❤️ for preserving precious family memories.