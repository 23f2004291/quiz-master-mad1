import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, request, render_template, redirect, url_for, flash, session

from models import User, Subject, Chapter, Quiz, Question, Score
from app import app,db
from datetime import datetime


@app.route('/')
def home():
    if 'user_id' not in session:
        flash("Please login to continue")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])  # Retrieve user from DB

    if user.role == 0:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))


@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()

    if username == "" or password == "":
        flash("Username and Password cannot be empty")
        return redirect(url_for("login"))
    
    if not user:
        flash("User does not exist")
        return redirect(url_for("login"))
    
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for("login"))
    
    session['user_id'] = user.id
    session['user_name'] = user.name  # Store username in session

    if user.role == 0:
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Login Successful")
        return redirect(url_for('user_dashboard'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logout Successful")
    return redirect(url_for('login'))
    
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=["POST"])
def register_post():
    username = request.form.get("username")
    name = request.form.get("name")
    password = request.form.get("password")
    qualification = request.form.get("qualification")
    dob_str = request.form.get("dob")
    dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    if User.query.filter_by(username=username).first():
        flash("User with this username already exists. Please choose another username")
        return redirect(url_for("register"))
    user = User(username=username, name=name, password=password, qualification=qualification, dob=dob)
    db.session.add(user)
    db.session.commit()

    flash("User Registered Successfully")
    return redirect(url_for("login"))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', name="Admin", subjects=Subject.query.all(), chapters=Chapter.query.all())

@app.route('/admin_dashboard/add_subject')
def add_subject():
    return render_template('/subject/add_subject.html')
@app.route('/admin_dashboard/add_subject', methods=["POST"])
def add_subject_post():
    action = request.form.get("action")  # Check which button was clicked

    if action == "Discard":
        flash("Subject creation discarded!", "warning")
        return redirect(url_for("admin_dashboard"))  # Redirect if Discard is clicked

    else:
        subject_name = request.form.get("subject_name", "").strip()
        description = request.form.get("description", "").strip()

        if not subject_name or not description:
            flash("Both Subject Name and Description are required!", "danger")
            return redirect(url_for("add_subject"))  # Redirect back to the form

        # Insert into the database
        new_subject = Subject(subject_name=subject_name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject Added Successfully!", "success")
        return redirect(url_for("admin_dashboard"))  # Redirect after adding

@app.route('/admin_dashboard/<int:subject_id>/edit_subject')
def edit_subject(subject_id):
    return render_template('subject/edit_subject.html', subject=Subject.query.get(subject_id))

@app.route('/admin_dashboard/<int:subject_id>/edit_subject', methods=["POST"])
def edit_subject_post(subject_id):
    subject = Subject.query.get_or_404(subject_id)  # Fetch the specific subject

    action = request.form.get("action")
    
    if action == "Discard":
        return redirect(url_for("admin_dashboard"))  # Redirect if Discard is clicked

    # Fetch form values safely
    subject_name = request.form.get("subject_name", "").strip()
    description = request.form.get("description", "").strip()

    if not subject_name:
        flash("Subject Name cannot be empty!", "danger")
        return redirect(url_for("edit_subject", subject_id=subject_id))

    
    subject.subject_name = subject_name
    subject.description = description
    db.session.commit()

    flash("Subject Updated Successfully!", "success")
    return redirect(url_for("admin_dashboard"))  # Redirect after saving


@app.route('/admin_dashboard/<int:subject_id>/delete_subject', methods=["POST"])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)  # Delete the subject
    db.session.commit()
    flash("Subject Deleted Successfully!", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_dashboard/<int:subject_id>/add_chapter')
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    return render_template('/chapter/add_chapter.html', subject=subject)

@app.route('/admin_dashboard/<int:subject_id>/add_chapter', methods=["POST"])
def add_chapter_post(subject_id):
    action = request.form.get("action")  # Get which button was clicked

    if action == "Discard":
        flash("Chapter creation discarded!", "warning")
        return redirect(url_for("admin_dashboard"))  # Redirect if Discard is clicked

    # Fetch form values
    chapter_name = request.form.get("chapter_name", "").strip()
    description = request.form.get("description", "").strip()

    # Validate form inputs
    if not chapter_name or not description:
        flash("Both Chapter Name and Description are required!", "danger")
        return redirect(url_for("add_chapter", subject_id=subject_id))  # Redirect back to form

    # Insert into the database
    new_chapter = Chapter(chapter_name=chapter_name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()

    flash("Chapter Added Successfully!", "success")
    return redirect(url_for("admin_dashboard"))  # Redirect after adding


@app.route('/admin_dashboard/<int:chapter_id>/edit_chapter')
def edit_chapter(chapter_id):
    return render_template('chapter/edit_chapter.html', chapter=Chapter.query.get(chapter_id))

@app.route('/admin_dashboard/<int:chapter_id>/edit_chapter', methods=["POST"])
def edit_chapter_post(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    action = request.form.get("action")
    if action == "Discard":
        return redirect(url_for("admin_dashboard"))
    chapter_name = request.form.get("chapter_name", "").strip()
    description = request.form.get("description", "").strip()

    if not chapter_name:
        flash("Chapter Name cannot be empty!", "danger")
        return redirect(url_for("edit_subject", chapter_id=chapter_id))

    
    chapter.chapter_name =chapter_name
    chapter.description = description
    db.session.commit()

    flash("Chapter Updated Successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route('/admin_dashboard/<int:chapter_id>/delete_chapter', methods=["POST"])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)  # Delete the chapter
    db.session.commit()
    flash("Chapter Deleted Successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/quiz')
def quiz():
    return render_template('quiz.html',name='Admin', quizzes=Quiz.query.all(), questions=Question.query.all(), subjects=Subject.query.all(), chapters=Chapter.query.all())

@app.route('/quiz/add_quiz')
def add_quiz():
    return render_template('add_quiz.html', chapters=Chapter.query.all())

@app.route('/quiz/add_quiz', methods=["POST"])
def add_quiz_post():
    action = request.form.get("action")

    if action == "Discard":
        flash("Quiz creation discarded!", "warning")
        return redirect(url_for("quiz"))
    else:
        chapter_id = request.form.get("chapter_id")
        date_of_quiz_str = request.form.get("date_of_quiz")
        hours = request.form.get("hours", 0)
        minutes = request.form.get("minutes", 0)
        difficulty_level = request.form.get("difficulty_level")

        # Convert to integer, defaulting to 0 if empty
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        time_duration = (hours * 60) + minutes

        if not chapter_id or not date_of_quiz_str or time_duration <= 0 or not difficulty_level:
            flash("All fields are required!", "danger")
            return redirect(url_for("add_quiz"))

        date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
        new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, difficulty_level=difficulty_level)

        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz Added Successfully!", "success")
        return redirect(url_for("quiz"))

@app.route('/quiz/<int:quiz_id>/edit_quiz')
def edit_quiz(quiz_id):
    return render_template('edit_quiz.html', quiz=Quiz.query.get(quiz_id), chapters=Chapter.query.all())

@app.route('/quiz/<int:quiz_id>/edit_quiz', methods=["POST"])
def edit_quiz_post(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    action = request.form.get("action")
    if action == "Discard":
        return redirect(url_for("quiz"))
    
    chapter_id = request.form.get("chapter_id")
    date_of_quiz_str = request.form.get("date_of_quiz")
    hours = request.form.get("hours", 0)
    minutes = request.form.get("minutes", 0)
    difficulty_level = request.form.get("difficulty_level")

    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    time_duration = (hours * 60) + minutes

    if not chapter_id or not date_of_quiz_str or time_duration <= 0 or not difficulty_level:
        flash("All fields are required!", "danger")
        return redirect(url_for("edit_quiz", quiz_id=quiz_id))
    
    date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
    quiz.chapter_id = chapter_id
    quiz.date_of_quiz = date_of_quiz
    quiz.time_duration = time_duration
    quiz.difficulty_level = difficulty_level
    db.session.commit()

    flash("Quiz Updated Successfully!", "success")
    return redirect(url_for("quiz"))

@app.route('/quiz/<int:quiz_id>/delete_quiz', methods=["POST"])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)  # Delete the quiz
    db.session.commit()
    flash("Quiz Deleted Successfully!", "success")
    return redirect(url_for('quiz'))


@app.route('/quiz/<int:quiz_id>/add_question')
def add_question(quiz_id):
    return render_template('add_question.html', quiz=Quiz.query.get(quiz_id))

@app.route('/quiz/<int:quiz_id>/add_question', methods=["POST"])
def add_question_post(quiz_id):
    action = request.form.get("action")

    if action == "Discard":
        flash("Question creation discarded!", "warning")
        return redirect(url_for("quiz"))
    else:
        question_text = request.form.get("question_text", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct_option = request.form.get("correct_option", "").strip()

        if not question_text or not option_a or not option_b or not option_c or not option_d or not correct_option:
            flash("All fields are required!", "danger")
            return redirect(url_for("add_question", quiz_id=quiz_id))

        new_question = Question(question_text=question_text, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d, correct_option=correct_option, quiz_id=quiz_id)

        db.session.add(new_question)
        db.session.commit()
        flash("Question Added Successfully!", "success")
        return redirect(url_for("quiz"))


@app.route('/quiz/<int:quiz_id>/edit_question/<int:question_id>')
def edit_question(quiz_id, question_id):
    return render_template('edit_question.html', question=Question.query.get(question_id), quiz=Quiz.query.get(quiz_id))

@app.route('/quiz/<int:quiz_id>/edit_question/<int:question_id>', methods=["POST"])
def edit_question_post(quiz_id, question_id):
    question = Question.query.get_or_404(question_id)
    action = request.form.get("action")
    if action == "Discard":
        return redirect(url_for("quiz"))
    
    question_text = request.form.get("question_text", "").strip()
    option_a = request.form.get("option_a", "").strip()
    option_b = request.form.get("option_b", "").strip()
    option_c = request.form.get("option_c", "").strip()
    option_d = request.form.get("option_d", "").strip()
    correct_option = request.form.get("correct_option", "").strip()

    if not question_text or not option_a or not option_b or not option_c or not option_d or not correct_option:
        flash("All fields are required!", "danger")
        return redirect(url_for("edit_question", quiz_id=quiz_id, question_id=question_id))
    
    question.question_text = question_text
    question.option_a = option_a
    question.option_b = option_b
    question.option_c = option_c
    question.option_d = option_d
    question.correct_option = correct_option
    db.session.commit()

    flash("Question Updated Successfully!", "success")
    return redirect(url_for("quiz"))

@app.route('/quiz/<int:quiz_id>/delete_question/<int:question_id>', methods=["POST"])
def delete_question(quiz_id, question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)  # Delete the question
    db.session.commit()
    flash("Question Deleted Successfully!", "success")
    return redirect(url_for('quiz'))

# user part begins here
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash("Please login to continue")
        return redirect(url_for('login'))
    
    name = session.get('user_name', 'User')  # Retrieve name from session
    return render_template(
        'user_dashboard.html', 
        name=name, 
        quizzes=Quiz.query.all(), 
        questions=Question.query.all(), 
        subjects=Subject.query.all(), 
        chapters=Chapter.query.all()
    )


# @app.route('/quiz/<int:quiz_id>/start_quiz')
# def start_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)  # Ensure quiz exists
#     questions = Question.query.filter_by(quiz_id=quiz_id).all()  # Fetch only relevant questions
#     return render_template('start_quiz.html', quiz=quiz, questions=questions)

@app.route('/quiz/<int:quiz_id>/start_quiz', methods=["GET"])
def start_quiz(quiz_id):
    if 'user_id' not in session:
        flash("Please login to continue")
        return redirect(url_for('login'))

    session[f'quiz_start_time_{quiz_id}'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")  # Convert to string

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('start_quiz.html', quiz=quiz, questions=questions)




from datetime import datetime

@app.route('/quiz/<int:quiz_id>/start_quiz', methods=["POST"])
def start_quiz_post(quiz_id):
    if 'user_id' not in session:
        flash("Please login to continue")
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    correct_answers = 0
    incorrect_answers = 0
    total_questions = len(questions)

    # Retrieve and check start time
    start_time_str = session.get(f'quiz_start_time_{quiz_id}')
    
    if not start_time_str:
        flash("Error: No start time recorded. Please try again.", "danger")
        return redirect(url_for('start_quiz', quiz_id=quiz_id))

    # Ensure it's a string before conversion
    if isinstance(start_time_str, datetime):
        start_time = start_time_str  # If it's already a datetime, use it
    else:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")  # Convert string to datetime

    end_time = datetime.utcnow()
    time_taken_seconds = int((end_time - start_time).total_seconds())

    # Convert time taken into MM:SS format
    minutes = time_taken_seconds // 60
    seconds = time_taken_seconds % 60
    time_taken = f"{minutes:02}:{seconds:02}"  # MM:SS format

    # Check user's answers
    for question in questions:
        user_answer = request.form.get(f"question_{question.id}")  # Fetch answer from form
        if user_answer == question.correct_option:
            correct_answers += 1
        else:
            incorrect_answers += 1

    # Calculate score
    total_scored = correct_answers
    percentage = round((total_scored / total_questions) * 100, 2) if total_questions > 0 else 0

    # Save score to database
    new_score = Score(
        quiz_id=quiz_id,
        user_id=session['user_id'],
        total_scored=total_scored,
        timestamp_of_attempt=end_time
    )
    db.session.add(new_score)
    db.session.commit()

    flash("Quiz Submitted Successfully!", "success")

    # Pass all required values to the result page
    return render_template("result.html",
                           quiz=quiz,
                           total_scored=total_scored,
                           total_questions=total_questions,
                           correct_answers=correct_answers,
                           incorrect_answers=incorrect_answers,
                           time_taken=time_taken,  # Pass formatted MM:SS time
                           percentage=percentage)



@app.route('/user_dashboard/scores')
def scores():
    name = session.get('user_name', 'User')
    return render_template('scores.html', name=name, scores=Score.query.filter_by(user_id=session['user_id']).all(), quizzes=Quiz.query.all())

@app.route('/user_dashboard/summary')
def summary():
    name = session.get('user_name', 'User')
    if 'user_id' not in session:
        flash("Please login to continue", "warning")
        return redirect(url_for('login'))

    scores = Score.query.filter_by(user_id=session['user_id']).all()

    score_chart_data = []  # Store (score, pie_chart) tuples

    for score in scores:
        correct_answers = score.total_scored
        incorrect_answers = len(score.quiz.questions) - correct_answers

        # Generate pie chart
        plt.figure(figsize=(3, 3))
        # labels = ['Correct', 'Incorrect']
        sizes = [correct_answers, incorrect_answers]
        colors = ['#1ca700','#e01212']  # Red and Green colors
        plt.pie(sizes, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.axis('equal')

        # Save to a bytes buffer
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        pie_chart_url = base64.b64encode(img.getvalue()).decode()

        # Append tuple (score, pie_chart_url) to list
        score_chart_data.append((score, f"data:image/png;base64,{pie_chart_url}"))

        plt.close()

    return render_template('summary.html', name=name, score_chart_data=score_chart_data)

@app.route('/admin_dashboard/summary')
def admin_summary():
    # Bar Chart Data - Frequency of Quiz Attempts
    quiz_attempts = db.session.query(Score.quiz_id, db.func.count(Score.quiz_id)).group_by(Score.quiz_id).all()
    
    quiz_labels = [f"Quiz {q_id}" for q_id, _ in quiz_attempts]
    quiz_counts = [count for _, count in quiz_attempts]

    # Generate Bar Chart
    plt.figure(figsize=(8, 4))
    plt.bar(quiz_labels, quiz_counts, color='#4CAF50')
    plt.xlabel("Quiz ID")
    plt.ylabel("No. of Attempts")
    plt.title("Frequency of Quiz Attempts")
    plt.xticks(rotation=45)

    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png', bbox_inches='tight')
    bar_img.seek(0)
    bar_chart_url = f"data:image/png;base64,{base64.b64encode(bar_img.getvalue()).decode()}"
    plt.close()

    # Pie Chart Data - Subject-wise No. of Quizzes
    subject_counts = db.session.query(Chapter.chapter_name, db.func.count(Quiz.id)).join(Quiz).group_by(Chapter.id).all()

    subject_labels = [subject for subject, _ in subject_counts]
    subject_quiz_counts = [count for _, count in subject_counts]

    # Generate Pie Chart
    plt.figure(figsize=(5, 5))
    plt.pie(subject_quiz_counts, labels=subject_labels, autopct='%1.1f%%', colors=['#FF5733', '#33B5FF', '#FFC300', '#4CAF50'])
    plt.title("Quizzes Per Subject")

    pie_img = io.BytesIO()
    plt.savefig(pie_img, format='png', bbox_inches='tight')
    pie_img.seek(0)
    pie_chart_url = f"data:image/png;base64,{base64.b64encode(pie_img.getvalue()).decode()}"
    plt.close()

    return render_template('admin_summary.html', name='Admin', bar_chart_url=bar_chart_url, pie_chart_url=pie_chart_url)

@app.route('/admin_dashboard/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()

    print(f"🔍 Received search query: '{query}'")  # Debugging statement

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('admin_dashboard'))

    # Search in database
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.subject_name.ilike(f"%{query}%")).all()  # Use ilike() for case-insensitive search
    chapters = Chapter.query.filter(Chapter.chapter_name.ilike(f"%{query}%")).all()
    
    try:
        quizzes = Quiz.query.filter(Quiz.id == query).all()  # Searching Quiz ID directly (ID is numeric)
    except Exception as e:
        print(f"Error in Quiz Search: {e}")  # Print error if there's any issue

    results = {
        "Users": users,
        "Subjects": subjects,
        "Chapters": chapters,
        "Quizzes": quizzes
    }

    if not any(results.values()):  # If all lists are empty
        print("🚫 No search results found.")

    return render_template('search_admin.html', query=query, results=results, name='Admin')







