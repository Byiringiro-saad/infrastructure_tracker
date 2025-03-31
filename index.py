import logging
import mysql.connector

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            user="root",
            password="root",
            host="localhost",
            database="infrastructure_db"
        )
        logging.info("Successfully connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None

def setup_database():
    conn = mysql.connector.connect(
        user="root",
        password="root"
        host="localhost",
    )
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS infrastructure_db;")
    cursor.execute("CREATE DATABASE infrastructure_db;")
    cursor.execute("USE infrastructure_db;")
    
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') NOT NULL DEFAULT 'user'
        );
    """)
    
    cursor.execute("""
        CREATE TABLE reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            issue_type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            location VARCHAR(255) NOT NULL,
            status ENUM('Pending', 'In Progress', 'Resolved') NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    conn.commit()
    
    logging.info("Database setup completed successfully")
    cursor.close()
    conn.close()

def signup():
    username = input("Enter username: ")
    password = input("Enter password: ")
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, password))
        conn.commit()
        logging.info("User signed up successfully!")
        cursor.close()
        conn.close()

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return user
    return None

def report_issue(user_id):
    issue_type = input("Enter issue type (Road Damage, Power Outage, Water Issue): ")
    description = input("Describe the issue: ")
    location = input("Enter location: ")
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reports (user_id, issue_type, description, location, status) VALUES (%s, %s, %s, %s, 'Pending')", (user_id, issue_type, description, location))
        conn.commit()
        logging.info("Issue reported successfully!")
        cursor.close()
        conn.close()

def admin_dashboard():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, issue_type, description, location, status FROM reports")
        reports = cursor.fetchall()
        for report in reports:
            print(f"ID: {report[0]}, Type: {report[1]}, Description: {report[2]}, Location: {report[3]}, Status: {report[4]}")
        report_id = input("Enter report ID to update status: ")
        new_status = input("Enter new status (Pending, In Progress, Resolved): ")
        cursor.execute("UPDATE reports SET status = %s WHERE id = %s", (new_status, report_id))
        conn.commit()
        logging.info("Report updated successfully!")
        cursor.close()
        conn.close()

def main():
    logging.basicConfig(level=logging.INFO)
    setup_database()
    while True:
        print("\n1. Sign Up\n2. Log In\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            signup()
        elif choice == "2":
            user = login()
            if user:
                user_id, role = user
                if role == "admin":
                    admin_dashboard()
                else:
                    report_issue(user_id)
            else:
                print("Invalid credentials!")
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()