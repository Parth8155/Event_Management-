# Event Management System

A comprehensive Django REST Framework API for managing events, RSVPs, reviews, and user invitations with JWT authentication.

## Features

- **User Management**: Registration, JWT authentication, user profiles
- **Event Management**: Create, read, update, delete events with public/private visibility
- **RSVP System**: Users can RSVP to events with status tracking
- **Review System**: Users can leave ratings and reviews for events
- **Invitation System**: Organizers can invite users to private events
- **Custom Permissions**: Secure access control for private events
- **Admin Panel**: Full Django admin interface for data management
- **Pagination & Filtering**: Efficient data handling with search and filters


## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API: http://127.0.0.1:8000/api/
   - Admin Panel: http://127.0.0.1:8000/admin/

## API Endpoints

### Authentication Endpoints
- `POST /api/register/` - User registration
- `POST /api/token/` - Obtain JWT access token
- `POST /api/token/refresh/` - Refresh JWT token

### Events CRUD Endpoints
- `GET /api/events/` - List events (shows public events + user's own events + events where user is invited)
- `POST /api/events/` - Create new event (authenticated users only)
- `GET /api/events/{event_id}/` - Get specific event details
- `PUT /api/events/{event_id}/` - Update event (organizer only)
- `PATCH /api/events/{event_id}/` - Partially update event (organizer only)
- `DELETE /api/events/{event_id}/` - Delete event (organizer only)

### Event Actions
- `POST /api/events/{event_id}/rsvp/` - Create/update RSVP for event
- `POST /api/events/{event_id}/update_rsvp/` - Update existing RSVP status
- `GET /api/events/{event_id}/reviews/` - List all reviews for event
- `POST /api/events/{event_id}/add_review/` - Add or update review for event (authenticated users)
- `POST /api/events/{event_id}/invite/` - Invite user to private event (organizer only)
- `GET /api/events/{event_id}/invitations/` - List invitations for event (organizer only)
- `POST /api/events/{event_id}/remove_invitation/` - Remove invitation from event (organizer only)

### Filtering & Search
- `GET /api/events/?location={location}` - Filter events by location
- `GET /api/events/?organizer={organizer_id}` - Filter events by organizer
- `GET /api/events/?search={query}` - Search events by title, location, or organizer username

## Authentication Methods

### Method 1: Django Admin Login (Recommended for Testing)
1. Go to `http://127.0.0.1:8000/admin/`
2. Login with any user credentials
3. Session cookie enables API access
4. Use `http://127.0.0.1:8000/api/` for browsable interface

### Method 2: JWT Tokens
1. Register: `POST /api/register/` with user details
2. Login: `POST /api/token/` with username/password
3. Use token in `Authorization: Bearer <token>` header

## Data Models

### User (Django Auth User + Profile)
**Fields:**
- `id`: Auto-generated primary key
- `username`: Unique username (required)
- `email`: Unique email address (required)
- `password`: Hashed password (required)
- `first_name`: Optional first name
- `last_name`: Optional last name
- `date_joined`: Auto-generated join date
- `is_active`: Account status

### UserProfile (extends User)
**Fields:**
- `user`: One-to-one relationship with User
- `full_name`: Optional full name
- `bio`: Optional biography text
- `location`: Optional location
- `profile_picture`: Optional image URL

### Event
**Fields:**
- `id`: Auto-generated primary key
- `title`: Event title (max 255 chars, required)
- `description`: Event description (text, required)
- `organizer`: Foreign key to User (auto-set to creator)
- `location`: Event location (max 255 chars, required)
- `start_time`: Event start datetime (required)
- `end_time`: Event end datetime (required)
- `is_public`: Boolean flag (default: true)
- `created_at`: Auto-generated creation timestamp
- `updated_at`: Auto-generated update timestamp

**Constraints:**
- Organizer automatically set to request user on creation
- Unique together: None

### RSVP (Response to Event)
**Fields:**
- `id`: Auto-generated primary key
- `event`: Foreign key to Event
- `user`: Foreign key to User
- `status`: Choice field with options:
  - "Going"
  - "Maybe"
  - "Not Going"
  - Default: "Going"

**Constraints:**
- Unique together: (event, user) - one RSVP per user per event

### Review (Event Feedback)
**Fields:**
- `id`: Auto-generated primary key
- `event`: Foreign key to Event
- `user`: Foreign key to User
- `rating`: Positive integer (1-5, validated)
- `comment`: Text comment (required)
- `created_at`: Auto-generated timestamp

**Constraints:**
- Unique together: (event, user) - one review per user per event

### Invitation (Private Event Access)
**Fields:**
- `id`: Auto-generated primary key
- `event`: Foreign key to Event
- `user`: Foreign key to User
- `invited_at`: Auto-generated invitation timestamp

**Constraints:**
- Unique together: (event, user) - one invitation per user per event

## Permissions & Access Control

### IsOrganizerOrPublicReadOnly (Default Event Permission)
**Read Access:**
- **Public Events**: All authenticated users can view
- **Private Events**: Only organizer and invited users can view

**Write Access:**
- Only event organizer can create, update, or delete events

### IsOrganizer (Strict Organizer-Only Access)
- Only the user who created the event can access
- Used for invitation management actions

### Action-Specific Permissions

| Endpoint | Permission | Access Control |
|----------|------------|----------------|
| `POST /api/events/` | IsAuthenticated | Any authenticated user can create events |
| `GET /api/events/` | IsAuthenticated | Shows public events + user's events + invited events |
| `GET /api/events/{id}/` | IsOrganizerOrPublicReadOnly | Public events: all users, Private: organizer + invited |
| `PUT/PATCH /api/events/{id}/` | IsOrganizerOrPublicReadOnly | Organizer only |
| `DELETE /api/events/{id}/` | IsOrganizerOrPublicReadOnly | Organizer only |
| `POST /api/events/{id}/rsvp/` | IsAuthenticated | Any authenticated user |
| `POST /api/events/{id}/update_rsvp/` | IsAuthenticated | User can only update their own RSVP |
| `GET /api/events/{id}/reviews/` | IsAuthenticated | Any authenticated user |
| `POST /api/events/{id}/add_review/` | IsAuthenticated | Any authenticated user (add or update review) |
| `POST /api/events/{id}/invite/` | IsAuthenticated + IsOrganizer | Event organizer only |
| `GET /api/events/{id}/invitations/` | IsAuthenticated + IsOrganizer | Event organizer only |
| `POST /api/events/{id}/remove_invitation/` | IsAuthenticated + IsOrganizer | Event organizer only |

### Authentication Requirements
- All endpoints except `/api/register/` require authentication
- JWT tokens or Django session authentication (admin login)
- Unauthenticated requests return 401 Unauthorized


### Manual Testing Steps
1. **Register Users**: Create multiple test users via `/api/register/`
2. **Obtain Tokens**: Get JWT tokens for different users via `/api/token/`
3. **Create Events**: 
   - Create public events (visible to all)
   - Create private events (invite-only)
4. **Test Permissions**: Try accessing private events without invitation (should fail)
5. **RSVP Testing**: RSVP to events with different statuses
6. **Update RSVPs**: Change RSVP status using update_rsvp endpoint
7. **Invitation Flow**:
   - Create private event as User A
   - Invite User B to the event
   - User B should now see the event in their list
   - User A can view/manage invitations
   - User A can remove invitations
8. **Review System**: Add reviews to events (if implemented)
9. **Admin Panel**: Use Django admin to manage all data
10. **Filtering**: Test location, organizer, and search filters

### Admin Panel Testing
- Access admin at `http://127.0.0.1:8000/admin/`
- Create/manage users, events, RSVPs, reviews, invitations
- Manually create invitations for testing private events
- View related objects and relationships

## Project Structure
```
event_management/
├── events/
│   ├── __init__.py
│   ├── models.py              # Data models (UserProfile, Event, RSVP, Review, Invitation)
│   ├── serializers.py         # API serializers for all models
│   ├── views.py               # API views (RegisterView, EventViewSet with actions)
│   ├── permissions.py         # Custom permissions (IsOrganizer, IsOrganizerOrPublicReadOnly)
│   ├── urls.py                # URL routing for events app
│   ├── admin.py               # Django admin configuration
│   ├── tests.py               # Unit tests
│   ├── apps.py
│   └── migrations/            # Database migrations
├── event_management/
│   ├── __init__.py
│   ├── settings.py            # Django settings with DRF, JWT, filters
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py
│   ├── asgi.py
│   └── __pycache__/
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
├── .gitignore                 # Git ignore rules
└── db.sqlite3                 # SQLite database (development)
```

## Technologies Used

- **Django 5.2.7**: High-level Python web framework
- **Django REST Framework 3.15**: Powerful API toolkit for Django
- **djangorestframework-simplejwt**: JWT authentication for DRF
- **django-filter**: Dynamic filtering for querysets
- **SQLite**: Lightweight database for development
- **Python 3.10+**: Programming language
- **Django Admin**: Built-in administrative interface
- **DRF Browsable API**: Interactive API documentation

## Dependencies (requirements.txt)
```
Django==5.2.7
djangorestframework==3.16.1
djangorestframework-simplejwt==5.5.1
django-filter==25.2
Pillow==10.4.0
```

---

Built with Django REST Framework for the Event Management Assignment.