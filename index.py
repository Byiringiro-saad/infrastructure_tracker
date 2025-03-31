import os
import logging
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
from mysql.connector import Error

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='infrastructure_tracker.log'
)

logger = logging.getLogger('infrastructure_tracker')

# Load environment variables from .env file
load_dotenv()

class InfrastructureTracker:
    def __init__(self):
        """Initialize database connection"""
        try:
            # Get database credentials from environment variables
            self.connection = mysql.connector.connect(
                user=os.getenv('DB_USER', 'root'),
                host=os.getenv('DB_HOST', 'localhost'),
                password=os.getenv('DB_PASSWORD', 'root'),
                database=os.getenv('DB_NAME', 'infrastructure_tracker')
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                logger.info("Successfully connected to MySQL database")
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            raise
            
    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logger.info("MySQL connection closed")
            
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        try:
            # Create users table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create issue_types table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS issue_types (
                type_id INT AUTO_INCREMENT PRIMARY KEY,
                type_name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            )
            """)
            
            # Create reports table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                type_id INT,
                description TEXT NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                address VARCHAR(255),
                status ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
                photo_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (type_id) REFERENCES issue_types(type_id)
            )
            """)
            
            # Create admin_actions table for tracking admin activities
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_actions (
                action_id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT NOT NULL,
                report_id INT NOT NULL,
                action_type ENUM('Status Change', 'Priority Update', 'Comment') NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(user_id),
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
            """)
            
            # Insert default issue types
            default_types = [
                ('Road Damage', 'Issues related to road conditions, potholes, or pavement problems'),
                ('Power Outage', 'Problems with electricity supply or infrastructure'),
                ('Water Issue', 'Problems with water supply, quality, or infrastructure')
            ]
            
            self.cursor.executemany("""
            INSERT IGNORE INTO issue_types (type_name, description) VALUES (%s, %s)
            """, default_types)
            
            self.connection.commit()
            logger.info("Database setup completed successfully")
            
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error setting up database: {e}")
            raise
    
    # User-related operations
    def register_user(self, username, password, email, is_admin=False):
        """Register a new user"""
        try:
            query = """
            INSERT INTO users (username, password, email, is_admin)
            VALUES (%s, %s, %s, %s)
            """
            # In a real application, password should be hashed
            self.cursor.execute(query, (username, password, email, is_admin))
            self.connection.commit()
            user_id = self.cursor.lastrowid
            logger.info(f"User registered successfully: {username}")
            return user_id
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error registering user: {e}")
            raise
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            self.cursor.execute(query, (username, password))
            user = self.cursor.fetchone()
            if user:
                logger.info(f"User authenticated: {username}")
                return user
            logger.warning(f"Failed authentication attempt for username: {username}")
            return None
        except Error as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    # Report-related operations
    def submit_report(self, user_id, type_id, description, latitude, longitude, address=None, photo_path=None):
        """Submit a new infrastructure issue report"""
        try:
            query = """
            INSERT INTO reports (user_id, type_id, description, latitude, longitude, address, photo_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (user_id, type_id, description, latitude, longitude, address, photo_path))
            self.connection.commit()
            report_id = self.cursor.lastrowid
            logger.info(f"Report submitted successfully: ID {report_id}")
            return report_id
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error submitting report: {e}")
            raise
    
    def get_reports(self, status=None, type_id=None, limit=100, offset=0):
        """Get infrastructure issue reports with optional filters"""
        try:
            query = """
            SELECT r.*, t.type_name, u.username
            FROM reports r
            JOIN issue_types t ON r.type_id = t.type_id
            JOIN users u ON r.user_id = u.user_id
            """
            params = []
            
            # Add filters if provided
            where_clauses = []
            if status:
                where_clauses.append("r.status = %s")
                params.append(status)
            if type_id:
                where_clauses.append("r.type_id = %s")
                params.append(type_id)
                
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            self.cursor.execute(query, params)
            reports = self.cursor.fetchall()
            return reports
        except Error as e:
            logger.error(f"Error retrieving reports: {e}")
            raise
    
    def get_report_by_id(self, report_id):
        """Get a specific report by ID"""
        try:
            query = """
            SELECT r.*, t.type_name, u.username
            FROM reports r
            JOIN issue_types t ON r.type_id = t.type_id
            JOIN users u ON r.user_id = u.user_id
            WHERE r.report_id = %s
            """
            self.cursor.execute(query, (report_id,))
            return self.cursor.fetchone()
        except Error as e:
            logger.error(f"Error retrieving report {report_id}: {e}")
            raise
            
    def update_report_status(self, report_id, status, admin_id):
        """Update the status of a report"""
        try:
            # Update report status
            query = "UPDATE reports SET status = %s WHERE report_id = %s"
            self.cursor.execute(query, (status, report_id))
            
            # Log admin action
            action_query = """
            INSERT INTO admin_actions (admin_id, report_id, action_type, details)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(action_query, (admin_id, report_id, 'Status Change', f"Status updated to {status}"))
            
            self.connection.commit()
            logger.info(f"Report {report_id} status updated to {status} by admin {admin_id}")
            return True
        except Error as e:
            self.connection.rollback()
            logger.error(f"Error updating report status: {e}")
            raise
    
    # Admin analytics functions
    def get_report_statistics(self):
        """Get basic statistics about reports"""
        try:
            stats = {}
            
            # Total reports by status
            self.cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM reports 
            GROUP BY status
            """)
            stats['by_status'] = self.cursor.fetchall()
            
            # Total reports by type
            self.cursor.execute("""
            SELECT t.type_name, COUNT(*) as count 
            FROM reports r
            JOIN issue_types t ON r.type_id = t.type_id
            GROUP BY t.type_name
            """)
            stats['by_type'] = self.cursor.fetchall()
            
            # Reports per day (last 30 days)
            self.cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM reports 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
            """)
            stats['daily'] = self.cursor.fetchall()
            
            return stats
        except Error as e:
            logger.error(f"Error getting report statistics: {e}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        # Initialize tracker and setup database
        tracker = InfrastructureTracker()
        tracker.setup_database()
        
        # Example: Register admin and regular user
        admin_id = tracker.register_user("admin", "adminpassword", "admin@example.com", is_admin=True)
        user_id = tracker.register_user("user1", "userpassword", "user1@example.com")
        
        # Example: Submit a report
        report_id = tracker.submit_report(
            user_id=user_id,
            type_id=1,  # Road Damage
            description="Large pothole on Main Street near the library",
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St"
        )
        
        # Example: Admin updates report status
        tracker.update_report_status(report_id, "In Progress", admin_id)
        
        # Example: Get all reports
        reports = tracker.get_reports()
        print(f"Total reports: {len(reports)}")
        
        # Example: Get statistics
        stats = tracker.get_report_statistics()
        print("Report statistics:", stats)
        
    except Exception as e:
        print(f"Error: {e}")