import os
import time
import logging
import getpass
import mysql.connector
from prettytable import PrettyTable
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal text
init()

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """Display an ASCII art banner for the application"""
    banner = f"""{Fore.CYAN}
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🏙️  COMMUNITY INFRASTRUCTURE REPORTING SYSTEM  🏙️     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}"""
    print(banner)

def connect_to_db():
    """Connect to MySQL database"""
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
        print(f"{Fore.RED}Database connection error: {err}{Style.RESET_ALL}")
        return None

def setup_database():
    """Set up the database schema and initial admin user"""
    try:
        conn = mysql.connector.connect(
            user="root",
            password="root",
            host="localhost",
        )
        
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS infrastructure_db;")
        cursor.execute("CREATE DATABASE infrastructure_db;")
        cursor.execute("USE infrastructure_db;")
        
        # Create users table with password hashing note
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Expanded reports table with timestamps and more status options
        cursor.execute("""
            CREATE TABLE reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                issue_type VARCHAR(100) NOT NULL,
                severity ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
                description TEXT NOT NULL,
                location VARCHAR(255) NOT NULL,
                status ENUM('Pending', 'In Progress', 'Resolved', 'Rejected') NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        # Create admin user
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        conn.commit()
        
        logging.info("Database setup completed successfully")
        print(f"{Fore.GREEN}Database setup completed successfully!{Style.RESET_ALL}")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"Error setting up database: {err}")
        print(f"{Fore.RED}Database setup error: {err}{Style.RESET_ALL}")

def loading_animation(message, duration=1.5):
    """Display a simple loading animation with a message"""
    print(f"\n{message}", end="")
    for _ in range(5):
        print(f"{Fore.YELLOW}.{Style.RESET_ALL}", end="", flush=True)
        time.sleep(duration/5)
    print()

def signup():
    """User registration function"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.CYAN}📝 USER REGISTRATION{Style.RESET_ALL}\n")
    
    while True:
        username = input(f"{Fore.WHITE}Enter username: {Style.RESET_ALL}")
        if not username:
            print(f"{Fore.RED}Username cannot be empty.{Style.RESET_ALL}")
            continue
        
        # Password with confirmation and hidden input
        while True:
            password = getpass.getpass(f"{Fore.WHITE}Enter password: {Style.RESET_ALL}")
            if not password:
                print(f"{Fore.RED}Password cannot be empty.{Style.RESET_ALL}")
                continue
                
            confirm_password = getpass.getpass(f"{Fore.WHITE}Confirm password: {Style.RESET_ALL}")
            if password != confirm_password:
                print(f"{Fore.RED}Passwords do not match. Try again.{Style.RESET_ALL}")
                continue
            break
        
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                # Check if username already exists
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print(f"{Fore.RED}Username already exists. Please choose another one.{Style.RESET_ALL}")
                    cursor.close()
                    conn.close()
                    continue
                
                # Insert new user
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, password))
                conn.commit()
                loading_animation("Creating account")
                print(f"{Fore.GREEN}✅ User registered successfully!{Style.RESET_ALL}")
                cursor.close()
                conn.close()
                input("\nPress Enter to continue...")
                return
            except mysql.connector.Error as err:
                logging.error(f"Error during registration: {err}")
                print(f"{Fore.RED}Error during registration: {err}{Style.RESET_ALL}")
                cursor.close()
                conn.close()
        break

def login():
    """User login function"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.CYAN}🔐 USER LOGIN{Style.RESET_ALL}\n")
    
    username = input(f"{Fore.WHITE}Enter username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.WHITE}Enter password: {Style.RESET_ALL}")
    
    loading_animation("Authenticating")
    
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            print(f"{Fore.GREEN}✅ Login successful! Welcome, {username}!{Style.RESET_ALL}")
            time.sleep(1)
            return user
        else:
            print(f"{Fore.RED}❌ Invalid username or password.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
    return None

def display_user_dashboard(user_id, username):
    """Display the user dashboard with options"""
    while True:
        clear_screen()
        display_banner()
        print(f"\n{Fore.CYAN}👤 USER DASHBOARD - Welcome, {username}!{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}1. 📝 Report New Issue{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. 📋 View My Reports{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. 🔙 Logout{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.WHITE}Choose an option: {Style.RESET_ALL}")
        
        if choice == "1":
            report_issue(user_id)
        elif choice == "2":
            view_my_reports(user_id)
        elif choice == "3":
            print(f"{Fore.GREEN}Logging out...{Style.RESET_ALL}")
            time.sleep(1)
            return
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")

def report_issue(user_id):
    """Submit a new infrastructure issue report"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.CYAN}📝 REPORT NEW ISSUE{Style.RESET_ALL}\n")
    
    # Issue type selection with icons
    print("Select issue type:")
    print(f"{Fore.YELLOW}1. 🛣️  Road Damage{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. 💡 Power Outage{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. 💧 Water Issue{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}4. 🚦 Traffic Signal Problem{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5. 🌳 Public Space Issue{Style.RESET_ALL}")
    
    issue_types = {
        "1": "Road Damage",
        "2": "Power Outage",
        "3": "Water Issue",
        "4": "Traffic Signal Problem",
        "5": "Public Space Issue"
    }
    
    issue_choice = input(f"\n{Fore.WHITE}Enter choice (1-5): {Style.RESET_ALL}")
    issue_type = issue_types.get(issue_choice, "Other")
    
    # Severity selection
    print("\nSelect severity level:")
    print(f"{Fore.GREEN}1. Low - Minor inconvenience{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Medium - Significant problem{Style.RESET_ALL}")
    print(f"{Fore.RED}3. High - Hazardous condition{Style.RESET_ALL}")
    print(f"{Fore.RED}4. Critical - Emergency situation{Style.RESET_ALL}")
    
    severity_types = {
        "1": "Low",
        "2": "Medium", 
        "3": "High",
        "4": "Critical"
    }
    
    severity_choice = input(f"\n{Fore.WHITE}Enter severity (1-4): {Style.RESET_ALL}")
    severity = severity_types.get(severity_choice, "Medium")
    
    description = input(f"\n{Fore.WHITE}Describe the issue in detail: {Style.RESET_ALL}")
    location = input(f"{Fore.WHITE}Enter location (address/coordinates): {Style.RESET_ALL}")
    
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO reports (user_id, issue_type, severity, description, location) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, issue_type, severity, description, location)
            )
            conn.commit()
            
            loading_animation("Submitting report")
            print(f"{Fore.GREEN}✅ Issue reported successfully!{Style.RESET_ALL}")
            
            # Get the report ID
            cursor.execute("SELECT LAST_INSERT_ID()")
            report_id = cursor.fetchone()[0]
            print(f"{Fore.CYAN}Your report ID is: {report_id}{Style.RESET_ALL}")
            
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")
        except mysql.connector.Error as err:
            logging.error(f"Error submitting report: {err}")
            print(f"{Fore.RED}Error submitting report: {err}{Style.RESET_ALL}")
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")

def view_my_reports(user_id):
    """View reports submitted by the current user"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.CYAN}📋 MY REPORTS{Style.RESET_ALL}\n")
    
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, issue_type, severity, description, location, status, created_at 
            FROM reports 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not reports:
            print(f"{Fore.YELLOW}You haven't submitted any reports yet.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        # Create a pretty table
        table = PrettyTable()
        table.field_names = ["ID", "Issue Type", "Severity", "Description", "Location", "Status", "Date"]
        
        # Add status colors
        status_colors = {
            "Pending": Fore.YELLOW,
            "In Progress": Fore.CYAN,
            "Resolved": Fore.GREEN,
            "Rejected": Fore.RED
        }
        
        for report in reports:
            # Truncate description if too long
            description = report[3][:30] + "..." if len(report[3]) > 30 else report[3]
            
            # Format date
            date = report[6].strftime("%Y-%m-%d")
            
            # Apply color to status
            status = report[5]
            colored_status = f"{status_colors.get(status, '')}{status}{Style.RESET_ALL}"
            
            table.add_row([
                report[0],
                report[1],
                report[2],
                description,
                report[4][:20] + "..." if len(report[4]) > 20 else report[4],
                colored_status,
                date
            ])
        
        print(table)
        
        while True:
            print(f"\n{Fore.YELLOW}1. View Report Details{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. Back to Dashboard{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.WHITE}Choose an option: {Style.RESET_ALL}")
            
            if choice == "1":
                report_id = input(f"{Fore.WHITE}Enter report ID to view details: {Style.RESET_ALL}")
                view_report_details(report_id, user_id)
            elif choice == "2":
                return
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

def view_report_details(report_id, user_id):
    """View detailed information about a specific report"""
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.issue_type, r.severity, r.description, r.location, r.status, 
                   r.created_at, r.updated_at, u.username
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = %s AND (r.user_id = %s OR (SELECT role FROM users WHERE id = %s) = 'admin')
        """, (report_id, user_id, user_id))
        
        report = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if report:
            clear_screen()
            display_banner()
            print(f"\n{Fore.CYAN}📄 REPORT DETAILS{Style.RESET_ALL}\n")
            
            # Status icon mapping
            status_icons = {
                "Pending": f"{Fore.YELLOW}⏳ Pending{Style.RESET_ALL}",
                "In Progress": f"{Fore.CYAN}🔄 In Progress{Style.RESET_ALL}",
                "Resolved": f"{Fore.GREEN}✅ Resolved{Style.RESET_ALL}",
                "Rejected": f"{Fore.RED}❌ Rejected{Style.RESET_ALL}"
            }
            
            # Severity icon mapping
            severity_icons = {
                "Low": f"{Fore.GREEN}🟢 Low{Style.RESET_ALL}",
                "Medium": f"{Fore.YELLOW}🟡 Medium{Style.RESET_ALL}",
                "High": f"{Fore.RED}🟠 High{Style.RESET_ALL}",
                "Critical": f"{Fore.RED}🔴 Critical{Style.RESET_ALL}"
            }
            
            print(f"Report ID: {report[0]}")
            print(f"Submitted by: {report[8]}")
            print(f"Issue Type: {report[1]}")
            print(f"Severity: {severity_icons.get(report[2], report[2])}")
            print(f"Status: {status_icons.get(report[5], report[5])}")
            print(f"Location: {report[4]}")
            print(f"Submitted on: {report[6].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Last updated: {report[7].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nDescription:")
            print(f"{Fore.WHITE}{report[3]}{Style.RESET_ALL}")
            
            input("\nPress Enter to go back...")
        else:
            print(f"{Fore.RED}Report not found or you don't have permission to view it.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")

def display_admin_dashboard(user_id, username):
    """Display the admin dashboard with options"""
    while True:
        clear_screen()
        display_banner()
        print(f"\n{Fore.MAGENTA}👑 ADMIN DASHBOARD - Welcome, {username}!{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}1. 📋 View All Reports{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. 🔍 Search Reports{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. 📊 Statistics{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. 👥 User Management{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5. 🔙 Logout{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.WHITE}Choose an option: {Style.RESET_ALL}")
        
        if choice == "1":
            admin_view_reports()
        elif choice == "2":
            admin_search_reports()
        elif choice == "3":
            admin_statistics()
        elif choice == "4":
            admin_user_management()
        elif choice == "5":
            print(f"{Fore.GREEN}Logging out...{Style.RESET_ALL}")
            time.sleep(1)
            return
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")

def admin_view_reports():
    """Admin function to view all reports"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.MAGENTA}📋 ALL REPORTS{Style.RESET_ALL}\n")
    
    print(f"Filter by status:")
    print(f"{Fore.YELLOW}1. All Reports{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Pending Reports{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. In Progress Reports{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}4. Resolved Reports{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5. Rejected Reports{Style.RESET_ALL}")
    
    filter_choice = input(f"\n{Fore.WHITE}Choose a filter: {Style.RESET_ALL}")
    
    status_filter = ""
    if filter_choice == "2":
        status_filter = "WHERE status = 'Pending'"
    elif filter_choice == "3":
        status_filter = "WHERE status = 'In Progress'"
    elif filter_choice == "4":
        status_filter = "WHERE status = 'Resolved'"
    elif filter_choice == "5":
        status_filter = "WHERE status = 'Rejected'"
    
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
            FROM reports r
            JOIN users u ON r.user_id = u.id
            {status_filter}
            ORDER BY r.created_at DESC
        """)
        
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not reports:
            print(f"{Fore.YELLOW}No reports found with the selected filter.{Style.RESET_ALL}")
            input("\nPress Enter to continue...")
            return
        
        table = PrettyTable()
        table.field_names = ["ID", "User", "Issue Type", "Severity", "Description", "Location", "Status", "Date"]
        
        # Add status colors
        status_colors = {
            "Pending": Fore.YELLOW,
            "In Progress": Fore.CYAN,
            "Resolved": Fore.GREEN,
            "Rejected": Fore.RED
        }
        
        # Add severity colors
        severity_colors = {
            "Low": Fore.GREEN,
            "Medium": Fore.YELLOW,
            "High": Fore.RED,
            "Critical": Fore.RED + Style.BRIGHT
        }
        
        for report in reports:
            # Truncate description if too long
            description = report[4][:20] + "..." if len(report[4]) > 20 else report[4]
            
            # Format date
            date = report[7].strftime("%Y-%m-%d")
            
            # Apply color to status
            status = report[6]
            colored_status = f"{status_colors.get(status, '')}{status}{Style.RESET_ALL}"
            
            # Apply color to severity
            severity = report[3]
            colored_severity = f"{severity_colors.get(severity, '')}{severity}{Style.RESET_ALL}"
            
            table.add_row([
                report[0],
                report[1],
                report[2],
                colored_severity,
                description,
                report[5][:15] + "..." if len(report[5]) > 15 else report[5],
                colored_status,
                date
            ])
        
        print(table)
        
        while True:
            print(f"\n{Fore.YELLOW}1. Update Report Status{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. View Report Details{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. Back to Admin Dashboard{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.WHITE}Choose an option: {Style.RESET_ALL}")
            
            if choice == "1":
                report_id = input(f"{Fore.WHITE}Enter report ID to update: {Style.RESET_ALL}")
                admin_update_report(report_id)
            elif choice == "2":
                report_id = input(f"{Fore.WHITE}Enter report ID to view details: {Style.RESET_ALL}")
                view_report_details(report_id, None)  # Admin can view any report
            elif choice == "3":
                return
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

def admin_update_report(report_id):
    """Admin function to update a report's status"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.MAGENTA}🔄 UPDATE REPORT STATUS{Style.RESET_ALL}\n")
    
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, issue_type, status FROM reports WHERE id = %s", (report_id,))
        report = cursor.fetchone()
        
        if not report:
            print(f"{Fore.RED}Report not found.{Style.RESET_ALL}")
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        print(f"Report ID: {report[0]}")
        print(f"Issue Type: {report[1]}")
        print(f"Current Status: {report[2]}")
        
        print(f"\nSelect new status:")
        print(f"{Fore.YELLOW}1. ⏳ Pending{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. 🔄 In Progress{Style.RESET_ALL}")
        print(f"{Fore.GREEN}3. ✅ Resolved{Style.RESET_ALL}")
        print(f"{Fore.RED}4. ❌ Rejected{Style.RESET_ALL}")
        
        status_choice = input(f"\n{Fore.WHITE}Enter choice (1-4): {Style.RESET_ALL}")
        
        status_map = {
            "1": "Pending",
            "2": "In Progress",
            "3": "Resolved",
            "4": "Rejected"
        }
        
        new_status = status_map.get(status_choice)
        if not new_status:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        try:
            cursor.execute("UPDATE reports SET status = %s WHERE id = %s", (new_status, report_id))
            conn.commit()
            
            loading_animation("Updating report status")
            print(f"{Fore.GREEN}✅ Report status updated successfully!{Style.RESET_ALL}")
            
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")
        except mysql.connector.Error as err:
            logging.error(f"Error updating report: {err}")
            print(f"{Fore.RED}Error updating report: {err}{Style.RESET_ALL}")
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")

def admin_search_reports():
    """Admin function to search reports by various criteria"""
    clear_screen()
    display_banner()
    print(f"\n{Fore.MAGENTA}🔍 SEARCH REPORTS{Style.RESET_ALL}\n")
    
    print(f"Search by:")
    print(f"{Fore.YELLOW}1. Report ID{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Username{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. Issue Type{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}4. Location{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}5. Date Range{Style.RESET_ALL}")
    
    search_choice = input(f"\n{Fore.WHITE}Choose a search method: {Style.RESET_ALL}")
    
    conn = connect_to_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    reports = []
    
    if search_choice == "1":
        report_id = input(f"{Fore.WHITE}Enter Report ID: {Style.RESET_ALL}")
        cursor.execute("""
            SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE r.id = %s
        """, (report_id,))
    
    elif search_choice == "2":
        username = input(f"{Fore.WHITE}Enter username: {Style.RESET_ALL}")
        cursor.execute("""
            SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE u.username LIKE %s
            ORDER BY r.created_at DESC
        """, (f"%{username}%",))
    
    elif search_choice == "3":
        print(f"\nSelect issue type:")
        print(f"{Fore.YELLOW}1. 🛣️  Road Damage{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. 💡 Power Outage{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. 💧 Water Issue{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. 🚦 Traffic Signal Problem{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5. 🌳 Public Space Issue{Style.RESET_ALL}")
        
        issue_types = {
            "1": "Road Damage",
            "2": "Power Outage",
            "3": "Water Issue",
            "4": "Traffic Signal Problem",
            "5": "Public Space Issue"
        }
        
        type_choice = input(f"\n{Fore.WHITE}Enter choice (1-5): {Style.RESET_ALL}")
        issue_type = issue_types.get(type_choice)
        
        if issue_type:
            cursor.execute("""
                SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
                FROM reports r
                JOIN users u ON r.user_id = u.id
                WHERE r.issue_type = %s
                ORDER BY r.created_at DESC
            """, (issue_type,))
        else:
            print(f"{Fore.RED}Invalid issue type selection.{Style.RESET_ALL}")
    
    elif search_choice == "4":
        location = input(f"{Fore.WHITE}Enter location keywords: {Style.RESET_ALL}")
        cursor.execute("""
            SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
            FROM reports r
            JOIN users u ON r.user_id = u.id
            WHERE r.location LIKE %s
            ORDER BY r.created_at DESC
        """, (f"%{location}%",))
    
    elif search_choice == "5":
        start_date = input(f"{Fore.WHITE}Enter start date (YYYY-MM-DD): {Style.RESET_ALL}")
        end_date = input(f"{Fore.WHITE}Enter end date (YYYY-MM-DD): {Style.RESET_ALL}")
        try:
            cursor.execute("""
                SELECT r.id, u.username, r.issue_type, r.severity, r.description, r.location, r.status, r.created_at 
                FROM reports r
                JOIN users u ON r.user_id = u.id
                WHERE DATE(r.created_at) BETWEEN %s AND %s
                ORDER BY r.created_at DESC
            """, (start_date, end_date))
        except mysql.connector.Error as err:
            logging.error(f"Error with date search: {err}")
            print(f"{Fore.RED}Error with date format. Use YYYY-MM-DD.{Style.RESET_ALL}")
            cursor.close()
            conn.close()
            input("\nPress Enter to continue...")
            return
    else:
        print(f"{Fore.RED}Invalid search method selected.{Style.RESET_ALL}")
        cursor.close()
        conn.close()
        input("\nPress Enter to continue...")
        return
        
    reports = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not reports:
        print(f"{Fore.YELLOW}No reports found matching your search criteria.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    # Display search results
    clear_screen()
    display_banner()
    print(f"\n{Fore.MAGENTA}🔍 SEARCH RESULTS{Style.RESET_ALL}\n")
    
    table = PrettyTable()
    table.field_names = ["ID", "User", "Issue Type", "Severity", "Description", "Location", "Status", "Date"]
    
    # Add status colors
    status_colors = {
        "Pending": Fore.YELLOW,
        "In Progress": Fore.CYAN,
        "Resolved": Fore.GREEN,
        "Rejected": Fore.RED
    }
    
    # Add severity colors
    severity_colors = {
        "Low": Fore.GREEN,
        "Medium": Fore.YELLOW,
        "High": Fore.RED,
        "Critical": Fore.RED + Style.BRIGHT
    }
    
    for report in reports:
        # Truncate description if too long
        description = report[4][:20] + "..." if len(report[4]) > 20 else report[4]
        
        # Format date
        date = report[7].strftime("%Y-%m-%d")
        
        # Apply color to status
        status = report[6]
        colored_status = f"{status_colors.get(status, '')}{status}{Style.RESET_ALL}"
        
        # Apply color to severity
        severity = report[3]
        colored_severity = f"{severity_colors.get(severity, '')}{severity}{Style.RESET_ALL}"
        
        table.add_row([
            report[0],
            report[1],
            report[2],
            colored_severity,
            description,
            report[5][:15] + "..." if len(report[5]) > 15 else report[5],
            colored_status,
            date
        ])
    
    print(table)
    print(f"\n{Fore.GREEN}Found {len(reports)} report(s) matching your search criteria.{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.YELLOW}1. Update Report Status{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. View Report Details{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. New Search{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. Back to Admin Dashboard{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.WHITE}Choose an option: {Style.RESET_ALL}")
        
        if choice == "1":
            report_id = input(f"{Fore.WHITE}Enter report ID to update: {Style.RESET_ALL}")
            admin_update_report(report_id)
            return
        elif choice == "2":
            report_id = input(f"{Fore.WHITE}Enter report ID to view details: {Style.RESET_ALL}")
            view_report_details(report_id, None)  # None for admin to view any report
        elif choice == "3":
            admin_search_reports()  # Start a new search
            return
        elif choice == "4":
            return
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")