from flask_sqlalchemy import SQLAlchemy
from app import app
from datetime import datetime

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)  # 0 for admin, 1 for user

    def check_password(self, password):
        return self.password == password

class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete", lazy=True)

class Chapter(db.Model):
    __tablename__ = "chapter"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete", lazy=True)


class Quiz(db.Model):
    __tablename__ = "quiz"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard', "",name="difficulty_levels"), nullable=False)

    

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Enum('A', 'B', 'C', 'D', name="correct_options"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    quiz = db.relationship('Quiz', backref=db.backref('questions', cascade="all, delete", lazy=True))

class Score(db.Model):
    __tablename__ = "score"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp_of_attempt = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)

    quiz = db.relationship('Quiz', backref=db.backref('scores', cascade="all, delete", lazy=True))
    user = db.relationship('User', backref=db.backref('scores', cascade="all, delete", lazy=True))

with app.app_context():
    # db.drop_all()
    db.create_all()
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        dob_str = "1999-01-01"
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        admin = User(username="admin", name="admin", password="admin", qualification="admin", dob=dob, role=0)
        db.session.add(admin)
        db.session.commit()


