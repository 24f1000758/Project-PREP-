from datetime import datetime  
from extension import db # Import the db instance from __init__.py

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # For email login
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)   # Hashed password
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    qualification = db.Column(db.String(100), nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    dob = db.Column(db.Date, nullable=True)

    # For Google login
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

    # Common
    login_method = db.Column(db.String(10), nullable=False)  # 'email' or 'google'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.full_name} ({self.email or self.google_id})>"


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deck_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Flashcard', backref='deck', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Deck {self.deck_name}>'

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    def __repr__(self):
        return f'<Flashcard {self.id}>'

class QuestionSet(db.Model):
    __tablename__ = 'question_set'
    id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(200), nullable=False)
    exam_date = db.Column(db.Date, nullable=True)
    exam_year = db.Column(db.Integer, nullable=True)
    subject = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the Question table
    questions = db.relationship('Question', backref='question_set', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<QuestionSet {self.set_name}>'


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question_set_id = db.Column(db.Integer, db.ForeignKey('question_set.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    negative_marks = db.Column(db.Float, default=0.0)
    explanation = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    passage_id = db.Column(db.Integer, db.ForeignKey('passage.id'), nullable=True)

    # One-to-Many relationships for different question types
    options = db.relationship('Option', backref='question', lazy=True, cascade="all, delete-orphan")
    match_items = db.relationship('MatchItem', backref='question', lazy=True, cascade="all, delete-orphan")
    sequence_items = db.relationship('SequenceItem', backref='question', lazy=True, cascade="all, delete-orphan")

    # One-to-One relationship for Assertion & Reasoning
    assertion_reason = db.relationship('AssertionReason', backref='question', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Question {self.id} - Type: {self.question_type}>'


class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    option_order = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Option {self.option_text[:20]}...>'


class AssertionReason(db.Model):
    __tablename__ = 'assertion_reason'
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    assertion_text = db.Column(db.Text, nullable=False)
    reason_text = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return f'<AssertionReason for Q_ID {self.question_id}>'


class MatchItem(db.Model):
    __tablename__ = 'match_item'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    column1_text = db.Column(db.Text, nullable=False)
    column2_text = db.Column(db.Text, nullable=False)
    is_correct_pair = db.Column(db.Boolean, nullable=False)
    group_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<MatchItem {self.column1_text[:10]}...>'


class SequenceItem(db.Model):
    __tablename__ = 'sequence_item'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    item_text = db.Column(db.Text, nullable=False)
    correct_order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<SequenceItem {self.item_text[:10]}...>'


class Passage(db.Model):
    __tablename__ = 'passage'
    id = db.Column(db.Integer, primary_key=True)
    passage_text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    
    # Relationship to the Question table (one passage can have many questions)
    questions = db.relationship('Question', backref='passage', lazy=True)

    def __repr__(self):
        return f'<Passage {self.title}>'