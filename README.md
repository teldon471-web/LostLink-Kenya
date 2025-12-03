# LostLink Kenya

![LostLink Kenya Banner](C:/Users/User/.gemini/antigravity/brain/a098a958-1acb-4335-a7b5-978ac16053da/lostlink_logo_banner_1764761368192.png)

> **Reuniting Communities, One Item at a Time**

LostLink Kenya is a community-driven web platform that helps people recover their lost items and reconnect with their belongings. Built with Django and modern web technologies, it provides a simple, secure, and effective way for Kenyans to report lost or found items and connect with each other.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

### Core Functionality
- **Post Lost/Found Items** - Users can create detailed posts about items they've lost or found
- **Advanced Search & Filtering** - Filter by category, location, item type, and status
- **Image Upload** - Support for uploading photos to help identify items
- **Location-Based** - Search for items in specific Kenya locations
- **User Profiles** - Personalized user accounts with profile management
- **Secure Authentication** - User registration, login, and password reset functionality
- **Email Notifications** - Password reset via email
- **Direct Contact** - Users can contact each other about matching items

### User Experience
- **Modern UI/UX** - Clean, intuitive interface with glassmorphism design
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- **Light Theme** - Beautiful peach-themed color scheme for better visibility
- **Fast Performance** - Optimized for quick loading and smooth interactions
- **Real-time Updates** - Recent activity feed on the landing page

### Categories Supported
- Electronics
- Documents
- Jewelry
- Vehicles
- Pets
- Clothing
- Money/Wallets
- Keys
- Phones
- Other

---

## Tech Stack

### Backend
- **Framework:** Django 5.2.8
- **Database:** SQLite (Development) / PostgreSQL (Production-ready)
- **Authentication:** Django Auth System
- **Image Processing:** Pillow 12.0.0
- **Server:** Gunicorn 23.0.0

### Frontend
- **HTML5 & CSS3** - Semantic markup and modern styling
- **Bootstrap 5.3.0** - Responsive grid system and components
- **JavaScript** - Interactive features
- **Font Awesome 6.4.0** - Icons
- **Google Fonts (Outfit)** - Typography

### Forms & UI
- **django-crispy-forms 2.1** - Beautiful form rendering
- **crispy-bootstrap5** - Bootstrap 5 template pack

### Development Tools
- **python-decouple 3.8** - Environment variable management
- **Git** - Version control

---

## Screenshots

### Landing Page
![Landing Page](C:/Users/User/.gemini/antigravity/brain/a098a958-1acb-4335-a7b5-978ac16053da/landing_page_final_1764761195641.png)

### Login Page
![Login Page](C:/Users/User/.gemini/antigravity/brain/a098a958-1acb-4335-a7b5-978ac16053da/login_page_peach_1764760654113.png)

### Footer
![Footer with Peach Background](C:/Users/User/.gemini/antigravity/brain/a098a958-1acb-4335-a7b5-978ac16053da/login_with_footer_1764760848891.png)

---

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git
- Virtual environment tool (venv)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/LostLink-Kenya.git
cd LostLink-Kenya
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```

### Step 5: Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## Usage

### For Users

#### Reporting a Lost Item
1. **Register/Login** to your account
2. Click **"Report Item"** or **"New Post"**
3. Fill in the details:
   - Title (e.g., "Lost iPhone 13 Pro")
   - Description
   - Select "Lost Item"
   - Choose category
   - Enter location
   - Upload photo (optional)
   - Date when item was lost
4. Click **"Submit"**

#### Reporting a Found Item
1. Follow the same steps as above
2. Select **"Found Item"** instead
3. Provide as many details as possible to help the owner identify it

#### Searching for Items
1. Go to **"Browse Items"** or **"Home"**
2. Use filters:
   - Search by keywords
   - Filter by item type (Lost/Found)
   - Filter by category
   - Filter by location
   - Filter by status (Active/Resolved)
3. Click on any item to view full details
4. Contact the poster if you have information

#### Managing Your Posts
- **View Your Posts:** Click on your username → View profile
- **Edit Post:** Go to post detail → Click "Edit"
- **Delete Post:** Go to post detail → Click "Delete"
- **Mark as Resolved:** Edit the post and change status to "Resolved"

### For Administrators

#### Access Admin Panel
Visit `http://127.0.0.1:8000/admin/` and login with superuser credentials.

#### Admin Capabilities
- Manage all users and posts
- Moderate content
- View statistics
- Manage categories
- Handle user reports

---

## Project Structure

```
LostLink-Kenya/
│
├── blog/                          # Main app for posts
│   ├── migrations/                # Database migrations
│   ├── static/blog/              # Static files (CSS, JS, images)
│   ├── templates/blog/           # HTML templates
│   │   ├── base.html            # Base template
│   │   ├── landing.html         # Landing page
│   │   ├── Home.html            # Posts listing
│   │   ├── about.html           # About page
│   │   ├── post_detail.html     # Single post view
│   │   ├── post_form.html       # Create/Edit post
│   │   └── ...
│   ├── models.py                 # Post model
│   ├── views.py                  # View logic
│   ├── urls.py                   # URL routing
│   ├── services.py               # Business logic
│   └── ...
│
├── users/                         # User authentication app
│   ├── migrations/
│   ├── templates/users/          # Auth templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── password_reset_*.html
│   ├── models.py                 # Profile model
│   ├── views.py                  # Auth views
│   ├── forms.py                  # User forms
│   ├── signals.py                # Auto-create profiles
│   └── ...
│
├── myproject/                     # Project settings
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL config
│   ├── wsgi.py                   # WSGI config
│   └── ...
│
├── media/                         # User-uploaded files
│   ├── post_pics/                # Post images
│   └── profile_pics/             # Profile pictures
│
├── staticfiles/                   # Collected static files
├── deploy/                        # Deployment configs
├── scripts/                       # Utility scripts
│
├── manage.py                      # Django management
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version
├── Procfile                       # Deployment config
├── db.sqlite3                     # SQLite database
└── README.md                      # This file
```

---

## Database Models

### Post Model
```python
class Post(models.Model):
    title = CharField(max_length=200)
    content = TextField()
    item_type = CharField(choices=['lost', 'found'])
    category = CharField(choices=[...])
    location = CharField(max_length=200)
    status = CharField(choices=['active', 'resolved'])
    image = ImageField(upload_to='post_pics/%Y/%m/%d/')
    date_posted = DateTimeField(default=timezone.now)
    date_item_lost_found = DateField(null=True, blank=True)
    author = ForeignKey(User, on_delete=CASCADE)
```

### Profile Model
```python
class Profile(models.Model):
    user = OneToOneField(User, on_delete=CASCADE)
    image = ImageField(default='default.jpg', upload_to='profile_pics')
    bio = TextField(max_length=500, blank=True)
```

---

## Configuration

### Email Configuration
For password reset functionality, configure email in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
```

**Note:** For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in `EMAIL_PASS`

### Static Files
```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Security Settings
For production, update:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'generate-a-strong-secret-key'
```

---

## Deployment

### Deployment Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up environment variables
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure media file storage
- [ ] Set up HTTPS/SSL
- [ ] Configure email backend
- [ ] Run `collectstatic`
- [ ] Run migrations on production database

### Deployment Platforms
This project is ready to deploy on:
- **Heroku** - Use included `Procfile` and `runtime.txt`
- **Railway** - Direct deployment from Git
- **Render** - Web service deployment
- **PythonAnywhere** - Django-friendly hosting
- **AWS/Azure/GCP** - Cloud platforms

### Sample Deployment Commands
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn server
gunicorn myproject.wsgi:application --bind 0.0.0.0:8000
```

---

## Contributing

We welcome contributions from the community! Here's how you can help:

### How to Contribute
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

### Areas for Contribution
- Bug fixes
- New features
- Documentation improvements
- UI/UX enhancements
- Translations
- Accessibility improvements

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

### Project Maintainer
- **Name:** Emmanuel
- **Email:** support@lostlink.ke
- **Location:** Nairobi, Kenya

### Support
- **Website:** [LostLink Kenya](http://lostlink.ke)
- **Email:** support@lostlink.ke
- **GitHub Issues:** [Report a bug](https://github.com/yourusername/LostLink-Kenya/issues)

### Social Media
- Twitter: [@LostLinkKenya](https://twitter.com/lostlinkkenya)
- Facebook: [LostLink Kenya](https://facebook.com/lostlinkkenya)
- Instagram: [@lostlinkkenya](https://instagram.com/lostlinkkenya)

---

## Acknowledgments

- **Bootstrap Team** - For the amazing CSS framework
- **Django Community** - For the robust web framework
- **Font Awesome** - For the beautiful icons
- **Google Fonts** - For the Outfit font family
- **eMobilis** - For the web development training
- **Community Contributors** - For making this project better

---

## Project Stats

- **Language:** Python
- **Framework:** Django
- **Version:** 1.0.0
- **Status:** Active Development
- **Last Updated:** December 2025

---

## Roadmap

### Version 1.1 (Planned)
- [ ] SMS notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Swahili, English)
- [ ] Integration with social media

### Version 1.2 (Future)
- [ ] AI-powered image matching
- [ ] Geolocation integration
- [ ] Reward system
- [ ] Community ratings and reviews
- [ ] API for third-party integrations

---

## FAQ

**Q: Is LostLink Kenya free to use?**  
A: Yes! LostLink Kenya is completely free for all users.

**Q: How long do posts stay active?**  
A: Posts remain active for 90 days by default, but you can mark them as resolved anytime.

**Q: Can I edit my post after publishing?**  
A: Yes, you can edit or delete your posts at any time from your profile.

**Q: Is my personal information safe?**  
A: Yes, we take privacy seriously. You control what information you share.

**Q: How do I prove ownership of a found item?**  
A: When contacted, you can describe unique identifying features to verify ownership.

---

<div align="center">

**Made with care in Kenya**

Star this repo if you find it helpful!

[Report Bug](https://github.com/yourusername/LostLink-Kenya/issues) · [Request Feature](https://github.com/yourusername/LostLink-Kenya/issues) · [Documentation](https://github.com/yourusername/LostLink-Kenya/wiki)

</div>
