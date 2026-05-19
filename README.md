# SMARTFIT GYM SYSTEM

## A. Contributor
Cody May Odhiambo

## B. Overview
A desktop-based gym management platform whereby admins log in to manage members, trainers, plans,
attendance, and payments — while members log in to view their profile, membership status, assigned
workouts, attendance history, and interact with a built-in fitness assistant chatbot.

## C. Installation
Follow these steps to set up and run the project locally:

**Clone the Repository**
```bash
git clone https://github.com/s1rcody69/SmartFit
cd SmartFit
```

**Install Dependencies**

The project requires Python 3.10 or later.
```bash
pip install tkinter
pip install Pillow
```

**Run the Application**
```bash
python main.py
```

The database is created automatically on first run.
A default admin account is seeded with the following credentials:
Username: admin
Password: admin123

## D. Usage

**Launch the App**
Run the Python file. You will be prompted to log in. If you do not have an account,
click the register link on the login screen to create a member account.

**Admin**
Log in as admin to access the full management dashboard. From here you can add and manage
members, register trainers, create membership plans, record payments, mark attendance,
and assign workout plans to members.

**Member**
Log in as a member to view your profile and BMI, check your membership status and expiry
date, view assigned workout plans, track your attendance history, and chat with the built-in
fitness assistant for workout tips, diet advice, and motivation.

## E. Features

**Role-Based Authentication**
Secure login system with password hashing. Users are redirected to their respective dashboards
based on their role — Admin or Member — upon successful login.

**Admin Dashboard**
The admin-facing side of SmartFit provides full gym management functionality through a clean
sidebar navigation with seven dedicated panels: Overview, Members, Trainers, Plans, Attendance,
Payments, and Workouts.

**GUI Architecture**
Utilizes Python's Tkinter with a single-window layout that swaps panel content dynamically
without spawning multiple windows, keeping the interface clean and responsive.

**Database Design**
SQLite relational backend with seven tables — users, members, trainers, plans, attendance,
payments, and workouts — connected through foreign key relationships for efficient data
retrieval and storage.

**Member Dashboard**
A personalized portal where members can view and edit their profile, monitor membership status
and expiry, review assigned workouts, track attendance visits, and access the fitness chatbot.

**Fitness Assistant Chatbot**
A rule-based conversational assistant built with OOP principles. It responds to fitness-related
keywords, suggests workout routines, recommends diet plans, calculates BMI from the member's
saved profile, and delivers motivational quotes.

**OOP Architecture**
The system is built on strong Object-Oriented Programming principles including inheritance
(Admin and Member both extend User), encapsulation (private role and password fields),
abstraction (base User class), and polymorphism (get_dashboard returns different values per role).

## F. Tech Stack

| Layer              | Technology                                                        |
|--------------------|-------------------------------------------------------------------|
| Environment        | Python 3.10+                                                      |
| GUI                | Tkinter                                                     |
| Database           | SQLite3                                                           |
| Password Security  | SHA-256 Hashing                                                   |
| OOP Models         | User, Admin, Member, Chatbot, FitnessAdvisor, ResponseManager     |