# 🎬 RGC Stream - Web Series Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF4B4B.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()

A comprehensive web series platform management system built with Streamlit and MySQL for CS-GY 6083 Database Systems project. Features include user authentication, series catalog management, feedback systems, contract management, and comprehensive analytics dashboards.

## 👥 Team RGC

- **Chahat Kothari** (ck3999)
- **Greeshma Hedvikar** (gh2461)
- **Rujuta Joshi** (rj2719)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [User Roles & Permissions](#-user-roles--permissions)
- [Core Functionalities](#-core-functionalities)
- [Database Schema](#-database-schema)
- [Security Features](#-security-features)
- [Stored Procedures](#-stored-procedures)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 Core Features
- **User Authentication System** with role-based access control (Viewer, Producer, Admin)
- **Interactive Series Catalog** with advanced search and filtering
- **Feedback & Review System** with rating management
- **Production Management** for producers and administrators
- **Contract Management** with payment tracking
- **Cast & Crew Association** management
- **Airing Schedule Management** with timeline visualization
- **Comprehensive Analytics Dashboard** with interactive charts
- **User Settings & Preferences** management

### 🎨 UI/UX Features
- Modern dark theme with gradient accents
- Responsive design with professional layouts
- Interactive carousel showcasing top series
- Real-time data visualization using Plotly
- Smooth animations and transitions
- Mobile-friendly interface

### 🔒 Security Features
- SHA-256 password hashing with salts
- SQL injection prevention via parameterized queries
- Input sanitization and validation
- Transaction management for data integrity
- Role-based access control
- Audit logging for sensitive operations

---

## 🏗 System Architecture

```
RGC Stream Application
│
├── Frontend Layer (Streamlit)
│   ├── Authentication Module
│   ├── Dashboard & Analytics
│   ├── Catalog Management
│   ├── User Settings
│   └── Admin Panel
│
├── Business Logic Layer (Python)
│   ├── User Management
│   ├── Series Management
│   ├── Contract Management
│   ├── Feedback System
│   └── Analytics Engine
│
└── Data Layer (MySQL)
    ├── Core Tables (Series, Episodes, Viewers)
    ├── Association Tables
    ├── Stored Procedures
    ├── Triggers & Views
    └── Audit Logging
```

---

## 📦 Prerequisites

### Software Requirements
- **Python**: 3.8 or higher
- **MySQL Server**: 8.0 or higher
- **pip**: Python package manager

### Hardware Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **Network**: Internet connection for external resources

---

## 🚀 Installation

### Step 1: Clone or Download Project Files

Ensure you have the following files:
- `rgc_stream_app.py` - Main application
- `stored_procedures_rgc.sql` - Database procedures
- `requirements.txt` - Python dependencies

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `streamlit==1.29.0` - Web application framework
- `mysql-connector-python==8.2.0` - MySQL database connector
- `pandas==2.1.4` - Data manipulation library
- `plotly==5.18.0` - Interactive visualization library

---

## 🗄 Database Setup

### Step 1: Create Database

```sql
-- Connect to MySQL as root or admin user
mysql -u root -p

-- Create database
CREATE DATABASE RGC;
USE RGC;
```

### Step 2: Import Base Schema

Import your existing database schema (from Part I of the project):

```sql
SOURCE path/to/your/schema.sql;
```

### Step 3: Execute Stored Procedures

```sql
SOURCE stored_procedures_rgc.sql;
```

This will create:
- 12 stored procedures for common operations
- 2 custom functions for calculations
- 5 triggers for audit logging
- 3 optimized views for queries
- Performance indexes
- Audit logging table

### Step 4: Verify Installation

```sql
-- Check stored procedures
SHOW PROCEDURE STATUS WHERE Db = 'RGC';

-- Check functions
SHOW FUNCTION STATUS WHERE Db = 'RGC';

-- Check triggers
SHOW TRIGGERS FROM RGC;

-- Check views
SHOW FULL TABLES WHERE Table_type = 'VIEW';
```

---

## ⚙️ Configuration

### Database Connection Setup

Open `rgc_stream_app.py` and update the database credentials (lines 121-126):

```python
connection = mysql.connector.connect(
    host='localhost',        # MySQL server address
    database='RGC',          # Database name
    user='your_username',    # UPDATE THIS
    password='your_password',# UPDATE THIS
    port=3306,              # Default MySQL port
    autocommit=False
)
```

### Security Configuration

The application uses the following security settings:

```python
# Password Salt (line 132)
salt = "streamvault_salt_2025"  # Change this for production

# Session timeout is handled by Streamlit
# Configure in .streamlit/config.toml if needed
```

---

## 🎮 Running the Application

### Start the Application

```bash
streamlit run rgc_stream_app.py
```

The application will automatically:
- Open in your default web browser
- Start on `http://localhost:8501`
- Display the login/registration page

### First-Time Setup

1. **Register a User Account**
   - Navigate to the "Register" tab
   - Fill in required information
   - Choose account type (default: VIEWER)
   - Optionally link to an existing viewer account

2. **Login**
   - Use your registered credentials
   - Access features based on your role

### Default Test Accounts (if using sample data)

Create test accounts or use existing viewer accounts from your database.

---

## 👤 User Roles & Permissions

### 🎭 Viewer Role
**Access:**
- Dashboard with personal statistics
- Browse series catalog
- Submit and view feedback/reviews
- Manage user settings and preferences
- View airing schedules
- Update profile information

**Restrictions:**
- Cannot modify series or episodes
- Cannot access admin functions
- Cannot manage contracts

### 🎬 Producer Role
**Access (All Viewer permissions plus):**
- Producer dashboard with analytics
- Contract management and tracking
- Payment tracking system
- Cast & crew management
- Airing schedule management
- Producer management
- Production house analytics

**Restrictions:**
- Limited admin panel access
- Cannot delete other users

### 👑 Admin Role
**Access (All permissions):**
- Full admin panel access
- Series management (add, edit, delete)
- Episode management
- Production house management
- Viewer account management
- Contract oversight
- System-wide analytics
- Audit log access

---

## 🔧 Core Functionalities

### 1. Dashboard & Analytics

**Features:**
- Real-time metrics (total series, episodes, viewers, avg rating)
- Genre distribution charts
- Geographic viewer distribution
- Top-rated series rankings
- Production house performance analytics
- Contract expiry warnings (Producer/Admin only)

**Technologies:**
- Plotly for interactive charts
- Pandas for data processing
- MySQL aggregate queries

### 2. Series Catalog

**Features:**
- Animated carousel of top 10 series
- Advanced search with filters (genre, name, rating)
- Sorting options (name, rating, episodes)
- Series cards with detailed information
- Language support (subtitles & dubbing)
- Series detail pages with episode listings

**Search Capabilities:**
- Full-text search on series names
- Genre filtering
- Sort by multiple criteria
- View count and rating display

### 3. Feedback System

**Features:**
- Submit reviews with 1-5 star ratings
- View all reviews with user information
- Duplicate prevention (one review per series per user)
- Real-time rating averages
- Review history tracking

**Business Logic:**
- Validates rating range (1-5)
- Prevents duplicate reviews
- Associates reviews with viewer accounts
- Calculates average ratings automatically

### 4. Producer Dashboard

**Features:**
- Contract overview and analytics
- Active contract value tracking
- Payment status monitoring
- Contract creation and management
- Payment tracking with status updates
- Contract expiry warnings

**Contract Management:**
- Contract types: Production, Distribution, Licensing, Talent
- Payment terms and milestones
- Status tracking: Active, Pending, Expired, Terminated
- Financial analytics

### 5. Cast & Crew Management

**Features:**
- Add actors, directors, writers, producers
- Role assignment with character names
- Compensation tracking
- Association status management
- Series-based filtering

**Role Types:**
- Actor, Director, Writer, Producer
- Cinematographer, Editor, Other
- Character association (for actors)

### 6. Schedule Management

**Features:**
- Episode airing schedule creation
- Platform assignment
- Date and time scheduling
- Duration management
- Timeline visualization
- Status tracking (Upcoming/Aired)

**Schedule Analytics:**
- 30-day timeline view
- Episodes per day count
- Upcoming schedule preview

### 7. Admin Panel

**Features:**
- Series CRUD operations
- Episode management
- Production house management
- Viewer account oversight
- Contract management
- System-wide analytics

**Safety Features:**
- Cascading delete with confirmation
- Transaction rollback on errors
- Deadlock prevention through ordered deletes

### 8. User Settings

**Features:**
- Profile management
- Address information updates
- Billing history view
- Payment method management
- Language preferences (subtitles/dubbing)
- Viewing preferences
- Privacy settings
- Activity tracking
- Achievement system

---

## 📊 Database Schema

### Core Tables

**RGC_WEB_SERIES**
- Series information and metadata
- Production house association
- Release information

**RGC_EPISODE**
- Episode details and titles
- Viewer statistics
- Technical interruption tracking

**RGC_VIEWER**
- Viewer account information
- Address and billing details
- Subscription management

**RGC_FEEDBACK**
- User reviews and ratings
- Series association
- Submission dates

**RGC_PRODUCTION_HOUSE**
- Production company information
- Location details

**RGC_CONTRACT** (If in your schema)
- Contract terms and conditions
- Financial information
- Date tracking

### Association Tables

- `RGC_WEB_SERIES_SERIES_TYPE` - Series genre associations
- `RGC_WEBSERIES_SUBTITLE` - Subtitle language mappings
- `RGC_WEBSERIES_DUBBING` - Dubbing language mappings
- `RGC_CAST_CREW` - Cast and crew associations
- `RGC_PRODUCER_PRODUCTION_HOUSE` - Producer relationships

### System Tables

**RGC_USERS** (Created by application)
- Authentication credentials
- User roles and types
- Account linking

**RGC_AUDIT_LOG** (Created by stored procedures)
- Operation tracking
- Change history
- User activity logs

---

## 🔐 Security Features

### Authentication

**Password Security:**
```python
# SHA-256 hashing with salt
password_hash = hashlib.sha256(f"{password}{salt}").hexdigest()
```

**Session Management:**
- Streamlit session state for user context
- Automatic logout functionality
- Role-based page access control

### SQL Injection Prevention

**Parameterized Queries:**
```python
query = "SELECT * FROM RGC_WEB_SERIES WHERE SERIES_ID = %s"
result = execute_query(query, (series_id,))
```

**Input Sanitization:**
```python
def sanitize_input(text):
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()
```

### Transaction Management

**ACID Compliance:**
```python
@contextmanager
def transaction():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        yield cursor
        conn.commit()
    except Error as e:
        conn.rollback()
        raise
```

### Concurrency Control

**Row Locking:**
```sql
-- In sp_update_episode_viewers
SELECT TOTAL_VIEWERS INTO v_current_viewers
FROM RGC_EPISODE
WHERE EPISODE_ID = p_episode_id
FOR UPDATE;  -- Locks row for concurrent access
```

---

## 📝 Stored Procedures

### Available Procedures

1. **sp_add_web_series** - Add new series with validation
2. **sp_delete_web_series** - Safe cascading delete
3. **sp_add_feedback** - Submit feedback with duplicate prevention
4. **sp_update_episode_viewers** - Concurrency-safe viewer updates
5. **sp_add_episode_with_schedule** - Atomic episode and schedule creation
6. **sp_get_series_statistics** - Comprehensive series stats
7. **sp_search_series** - Advanced series search
8. **sp_update_viewer_subscription** - Update subscription with audit
9. **sp_get_contract_analytics** - Contract analytics
10. **sp_get_producer_houses** - Producer-house associations

### Custom Functions

**fn_get_series_avg_rating(series_id)**
- Returns average rating for a series
- Returns 0 if no ratings exist

**fn_get_series_total_viewers(series_id)**
- Returns total viewers across all episodes
- Returns 0 if no episodes exist

### Usage Examples

```sql
-- Get series statistics
CALL sp_get_series_statistics('S001');

-- Search for series
CALL sp_search_series('Stranger', 'Drama', 4.0, 'United States');

-- Add feedback
CALL sp_add_feedback('F001', 'Great series!', 5, 'S001', 'A001');

-- Get contract analytics
CALL sp_get_contract_analytics('PH001');
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**

```
Error: Database Connection Error: Access denied for user
```

**Solution:**
- Verify MySQL credentials in `rgc_stream_app.py` (lines 121-126)
- Ensure MySQL server is running
- Check user permissions: `GRANT ALL PRIVILEGES ON RGC.* TO 'username'@'localhost';`

**2. Import Error: Module not found**

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
pip install -r requirements.txt
```

**3. Port Already in Use**

```
Error: Port 8501 is already in use
```

**Solution:**
```bash
# Use a different port
streamlit run rgc_stream_app.py --server.port 8502
```

**4. Stored Procedure Errors**

```
Error: Procedure doesn't exist
```

**Solution:**
```sql
-- Verify procedures exist
SHOW PROCEDURE STATUS WHERE Db = 'RGC';

-- Re-run stored procedures script
SOURCE stored_procedures_rgc.sql;
```

**5. Deadlock During Series Deletion**

**Solution:**
The stored procedures implement ordered deletes to prevent deadlocks. If issues persist:
```sql
-- Check for locked tables
SHOW PROCESSLIST;

-- Kill blocking processes if necessary
KILL <process_id>;
```

**6. Image Loading Issues in Carousel**

**Solution:**
Ensure internet connectivity as carousel uses external image URLs. Images are loaded from CDN sources.

### Debug Mode

Enable debug mode for detailed error messages:

```bash
streamlit run rgc_stream_app.py --logger.level=debug
```

### Database Reset

If you need to reset the database:

```sql
-- Drop all tables (be careful!)
DROP DATABASE RGC;
CREATE DATABASE RGC;
USE RGC;

-- Re-import schema and procedures
SOURCE your_schema.sql;
SOURCE stored_procedures_rgc.sql;
```

---

## 📁 Project Structure

```
RGC_Stream_Project/
│
├── rgc_stream_app.py              # Main application file
├── stored_procedures_rgc.sql      # Database procedures & functions
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── .streamlit/                    # Streamlit configuration (optional)
│   └── config.toml               # App settings
│
└── venv/                         # Virtual environment (created during setup)
```

### Key Code Sections in rgc_stream_app.py

**Lines 1-50:** Imports and configuration  
**Lines 51-350:** Custom CSS styling  
**Lines 351-395:** Carousel data and images  
**Lines 396-450:** Database connection and security functions  
**Lines 451-550:** User management and authentication  
**Lines 551-650:** Session state initialization  
**Lines 651-800:** Authentication page  
**Lines 801-1100:** Contract and payment management  
**Lines 1101-1400:** Association management (cast & crew)  
**Lines 1401-1600:** Producer management  
**Lines 1601-1900:** Schedule management  
**Lines 1901-2200:** Dashboard and analytics  
**Lines 2201-2500:** Producer dashboard  
**Lines 2501-2800:** Series catalog  
**Lines 2801-3000:** Series details  
**Lines 3001-3200:** Feedback system  
**Lines 3201-3800:** Admin panel  
**Lines 3801-4200:** User settings  
**Lines 4201-4300:** Main application logic

---

## 🤝 Contributing

This is an academic project for CS-GY 6083. If you're extending this project:

### Development Guidelines

1. **Code Style**: Follow PEP 8 for Python code
2. **SQL Style**: Use uppercase for SQL keywords
3. **Comments**: Document complex logic and business rules
4. **Security**: Always use parameterized queries
5. **Transactions**: Wrap multi-step operations in transactions

### Adding New Features

1. Define database requirements (tables, procedures)
2. Update stored procedures if needed
3. Implement backend logic in Python
4. Create Streamlit UI components
5. Add proper error handling
6. Test with different user roles
7. Update documentation

### Testing Checklist

- [ ] Database connection works
- [ ] Authentication functions correctly
- [ ] All user roles have appropriate access
- [ ] CRUD operations work properly
- [ ] Transactions commit/rollback correctly
- [ ] Error messages are user-friendly
- [ ] UI is responsive
- [ ] Charts and visualizations load
- [ ] Search and filters work
- [ ] Settings persist correctly

---

## 📚 Additional Resources

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)

### MySQL Resources
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MySQL Stored Procedures](https://dev.mysql.com/doc/refman/8.0/en/stored-programs.html)

### Python Libraries
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)

---

## 📄 License

This project is developed for academic purposes as part of CS-GY 6083 Database Systems course.

---

## 📞 Support

For questions or issues related to this project:

**Team RGC:**
- Chahat Kothari (ck3999)
- Greeshma Hedvikar (gh2461)
- Rujuta Joshi (rj2719)

**Course:** CS-GY 6083 - Database Systems  
**Institution:** New York University

---

## 🎓 Academic Integrity

This project is submitted as part of CS-GY 6083 coursework. Please respect academic integrity policies if referencing or building upon this work.

---

## 🔄 Version History

**Version 1.0** (Current)
- Initial release with complete functionality
- User authentication system
- Series catalog and management
- Feedback system
- Producer and admin dashboards
- Contract management
- Cast & crew management
- Schedule management
- Analytics and reporting
- User settings and preferences

---

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] Email notification system
- [ ] Advanced recommendation engine
- [ ] Video streaming integration
- [ ] Social features (friends, sharing)
- [ ] Mobile application
- [ ] Advanced analytics with ML
- [ ] Multi-language UI support
- [ ] Export reports to PDF
- [ ] API for third-party integrations
- [ ] Real-time chat support

---

## ✅ Acknowledgments

- **Streamlit Team** for the excellent web framework
- **MySQL Team** for the robust database system
- **Plotly Team** for visualization libraries
- **Course Instructors** for project guidance
- **Team RGC** for collaborative development

---

## 📊 Project Statistics

- **Total Lines of Code:** ~4,300
- **Python Functions:** 45+
- **Stored Procedures:** 12
- **Custom Functions:** 2
- **Database Triggers:** 4
- **Optimized Views:** 3
- **User Roles:** 3
- **Main Features:** 8+

---

**Built with ❤️ by Team RGC**

*For NYU CS-GY 6083 Database Systems*