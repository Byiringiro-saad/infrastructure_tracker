# Community Infrastructure Reporting System

A terminal-based application for reporting and tracking infrastructure issues within a community. This system allows community members to report various infrastructure problems and administrators to manage these reports.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Database Structure](#database-structure)
  - [Users Table](#users-table)
  - [Reports Table](#reports-table)
- [Application Flow](#application-flow)
- [Security Notes](#security-notes)

## Features

- **User Management**

  - User registration and login
  - Role-based access control (admin and regular users)

- **User Features**

  - Report infrastructure issues
  - Track status of submitted reports
  - View detailed report information

- **Admin Features**

  - View all reports
  - Search reports by various criteria
  - Update report status
  - View system statistics
  - Manage users

- **Issue Categories**
  - Road Damage
  - Power Outage
  - Water Issue
  - Traffic Signal Problem
  - Public Space Issue

## Requirements

- Python 3.x
- MySQL Server
- Required Python packages:
  - mysql-connector-python
  - prettytable
  - colorama

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/Byiringiro-saad/infrastructure_tracker
   cd infrastructure_tracker
   ```

2. Install the required Python packages:

   ```
   pip install mysql-connector-python prettytable colorama
   ```

3. Configure MySQL:
   - Ensure MySQL server is running
   - Update database connection parameters in `index.py` if necessary:
     - For regular connection (in `connect_to_db()` function)
     - For database setup (in `setup_database()` function)

## Usage

1. Run the application:

   ```
   python index.py
   ```

2. At first run, select 'y' when asked to set up the database.

3. Use the following credentials for to access admin account:

   - Username: `admin`
   - Password: `admin123`

4. Navigate through the application using the numeric menu options.

## Database Structure

The application uses two main tables:

### Users Table

- id (Primary Key)
- username (Unique)
- password
- role (user/admin)
- created_at

### Reports Table

- id (Primary Key)
- user_id (Foreign Key)
- issue_type
- severity (Low/Medium/High/Critical)
- description
- location
- status (Pending/In Progress/Resolved/Rejected)
- created_at
- updated_at

## Application Flow

1. **Login/Registration**: Users can log in or register for a new account
2. **Dashboard**: Different dashboards for users and admins
3. **Issue Reporting**: Users can report new infrastructure issues and insert pictures if necessary.
4. **Issue Tracking**: Both users and admins can track the status of reports
5. **Admin Management**: Admins can manage reports and users

## Security Notes

- **Password Security**: Currently, passwords are stored without hashing. This is a security risk, and we recommend implementing a hashing mechanism like `bcrypt` to securely store user passwords.
- **Database Credentials**: Database credentials are hardcoded in the application, which poses a security risk. A better approach is to use environment variables (`.env` file) to store credentials securely.
- **Input Validation**: Currently, there is limited input validation. Implementing stricter validation can prevent SQL injection and other security vulnerabilities.
