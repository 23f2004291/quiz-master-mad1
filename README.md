# quiz-master-mad1 (Quiz Master - V1)

## 📌 Project Overview
Quiz Master - V1 is a **multi-user exam preparation web application** built using Flask. It allows **admins to create quizzes** and **users to attempt them**, making learning interactive and structured. The platform includes **role-based access, quiz management, real-time scoring, and performance tracking.**

## ✨ Features
- 🏷️ **User & Admin Authentication** (Login, Register)
- 📚 **Subject & Chapter Management** (Admins can organize content and perform CRUD operations)
- 📝 **Quiz Creation & Management** (Admins can create quizzes and add questions)
- 🎯 **Taking a Quiz** (Users attempt quizzes with a timer)
- 📊 **Performance Tracking** (Users can view their quiz history)
- 🔍 **Search Functionality** (Find subjects, chapters, and quizzes quickly)
- 🏆 **Summary Feature** (Displays graphical representation of user's performance and other data)

## 🛠️ Tech Stack
- **Backend:** Flask, SQLite
- **Frontend:** HTML, CSS, Bootstrap, Jinja2
- **Other:** Flask-SQLAlchemy

## 🚀 Installation & Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/quiz-master-v1.git
   cd quiz-master-v1
   ```
2. **Create a Virtual Environment** (Optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```bash
   flask run
   ```
5. Open in browser: `http://127.0.0.1:5000/`

## 📂 Project Structure
```
quiz-master-v1/
│-- static/ (CSS, JS, Images)
│-- templates/ (HTML Templates)
│-- models.py (Database Models)
│-- controllers.py (Flask Routes)
│-- config.py (Configuration Settings)
│-- app.py (Entry Point)
│-- requirements.txt (Dependencies)
```

## ⚡ Usage Guide
- **Admin Login:** Create quizzes, manage subjects, and track user performance.
- **User Login:** Attempt quizzes, view results, and check rankings.
- **Search Bar:** Quickly find subjects, chapters, and quizzes.

🔗 **GitHub Repository:** [https://github.com/23f2004291/quiz-master-mad1]

