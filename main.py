import sqlite3
import random
import re
from getpass import getpass

# Database Setup
def initialize_database():
    conn = sqlite3.connect('banking_system.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        account_number TEXT UNIQUE NOT NULL,
        dob TEXT NOT NULL,
        city TEXT NOT NULL,
        password TEXT NOT NULL,
        balance REAL NOT NULL,
        contact_number TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    ''')

    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

# Utility Functions
def generate_account_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def validate_email(email):
    return re.match(r'^[\w\.]+@[\w]+\.[a-z]{2,3}$', email)

def validate_password(password):
    return re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password)

def validate_contact(contact):
    return re.match(r'^\d{10}$', contact)

# Input Simulation for Sandbox Environments
def safe_input(prompt):
    try:
        return input(prompt)
    except OSError:
        return ""

# Banking Functions
def add_user():
    name = safe_input("Enter Name: ")
    dob = safe_input("Enter Date of Birth (YYYY-MM-DD): ")
    city = safe_input("Enter City: ")
    address = safe_input("Enter Address: ")
    contact = safe_input("Enter Contact Number: ")
    if not validate_contact(contact):
        print("Invalid contact number! Must be 10 digits.")
        return

    email = safe_input("Enter Email ID: ")
    if not validate_email(email):
        print("Invalid email format!")
        return

    password = getpass("Create Password: ")
    if not validate_password(password):
        print("Password must contain at least 8 characters, including uppercase, lowercase, a number, and a special character.")
        return

    balance = float(safe_input("Enter Initial Balance (Minimum 2000): ") or 0)
    if balance < 2000:
        print("Initial balance must be at least 2000.")
        return

    account_number = generate_account_number()

    conn = sqlite3.connect('banking_system.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, account_number, dob, city, password, balance, contact, email, address))
        conn.commit()
        print(f"User created successfully!\n\nYour Details:\nName: {name}\nAccount Number: {account_number}\nDOB: {dob}\nCity: {city}\nContact: {contact}\nEmail: {email}\nAddress: {address}\nBalance: {balance}")
    except sqlite3.IntegrityError:
        print("Error: Account number already exists.")
    finally:
        conn.close()

def show_users():
    account_number = safe_input("Enter Account Number to view details (leave blank to view all users): ")
    conn = sqlite3.connect('banking_system.db')
    cursor = conn.cursor()

    if account_number:
        cursor.execute('SELECT * FROM users WHERE account_number = ?', (account_number,))
    else:
        cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()

    if not users:
        print("No user found.")
    else:
        for user in users:
            print(f"\nName: {user[1]}\nAccount Number: {user[2]}\nDOB: {user[3]}\nCity: {user[4]}\nBalance: {user[6]}\nContact: {user[7]}\nEmail: {user[8]}\nAddress: {user[9]}\nStatus: {'Active' if user[10] else 'Inactive'}")

    conn.close()

def login():
    account_number = safe_input("Enter Account Number: ")
    password = getpass("Enter Password: ")

    conn = sqlite3.connect('banking_system.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE account_number = ? AND password = ?', (account_number, password))
    user = cursor.fetchone()

    if user:
        print(f"Welcome {user[1]}!")
        while True:
            print("\n1. Show Balance\n2. Credit Amount\n3. Debit Amount\n4. Transfer Amount\n5. Change Password\n6. Update Profile\n7. Logout")
            try:
                choice = int(safe_input("Enter choice: ") or 0)
            except ValueError:
                print("Invalid input! Please enter a number.")
                continue

            if choice == 1:
                print(f"Current Balance: {user[6]}")

            elif choice == 2:
                amount = float(safe_input("Enter amount to credit: ") or 0)
                new_balance = user[6] + amount
                cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_balance, account_number))
                cursor.execute('INSERT INTO transactions (account_number, type, amount) VALUES (?, ?, ?)', (account_number, 'credit', amount))
                conn.commit()
                print("Amount credited successfully!")

            elif choice == 3:
                amount = float(safe_input("Enter amount to debit: ") or 0)
                if amount > user[6]:
                    print("Insufficient balance!")
                else:
                    new_balance = user[6] - amount
                    cursor.execute('UPDATE users SET balance = ? WHERE account_number = ?', (new_balance, account_number))
                    cursor.execute('INSERT INTO transactions (account_number, type, amount) VALUES (?, ?, ?)', (account_number, 'debit', amount))
                    conn.commit()
                    print("Amount debited successfully!")

            elif choice == 7:
                print("Logging out...")
                break

            else:
                print("Invalid choice!")
    else:
        print("Invalid account number or password!")

    conn.close()

# Main Menu
def main():
    initialize_database()

    while True:
        print("\n1. Add User\n2. Show Users\n3. Login\n4. Exit")
        try:
            choice = int(safe_input("Enter your choice: ") or 0)
        except ValueError:
            print("Invalid input! Please enter a number.")
            continue

        if choice == 1:
            add_user()
        elif choice == 2:
            show_users()
        elif choice == 3:
            login()
        elif choice == 4:
            print("Exiting application...")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
