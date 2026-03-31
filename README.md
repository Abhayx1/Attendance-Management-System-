# AI-Powered Attendance Management System

This is a full-stack real-time attendance system utilizing Facial Recognition with built-in Anti-Spoofing.

## Features
- **Face Registration**: Register employees with a single picture.
- **Real-Time Recognition**: Match faces quickly from live streams.
- **Anti-Spoofing**: Built-in DeepFace module (FasNet) protects against photo/video spoofing attempts.
- **Admin Dashboard**: View statistics, attendance rate, and recent check-ins in a sleek Premium UI.
- **Micro-Animations & Glassmorphism**: High-quality modern dark-mode aesthetics.

## Project Structure
- `backend/`: Contains the Flask API, logic, and SQLAlchemy Database definitions.
- `database/`: Stores the local SQLite database (`attendance.db`).
- `frontend/`: Contains the HTML, JS, and CSS files serving the dashboard.
- `models/users/`: Saves registered employee face embeddings/images.
- `utils/`: Contains the `DeepFace` AI wrapper logic for extracting and matching.

## Prerequisites
- Python 3.8+ (Tested with Python 3.11)
- A working webcam.

## Installation & Setup

1. Activate the Virtual Environment:
   .\venv\Scripts\activate

2. Start the Application:
   python backend/app.py

3. Access the Application:
   http://localhost:5000

## Usage Guide
1. Register a User
2. Mark Attendance
3. Use Admin Dashboard