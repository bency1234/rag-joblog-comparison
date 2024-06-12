from sqlalchemy import func

from .db import db

user_id = "users.id"


class ChatbotData(db.Model):
    __tablename__ = "chatbot_datas"

    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey(user_id))
    prompt = db.Column(db.Text())
    message_log = db.Column(db.Text())
    final_response = db.Column(db.Text())
    source_documents = db.Column(db.Text())
    response_time = db.Column(db.SmallInteger)
    exchange_cost = db.Column(db.Numeric(5, 3))
    is_evaluated = db.Column(db.Boolean, default=False)
    time_stamp = db.Column(db.DateTime())
    use_rag = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey("chatbot_datas.id"))
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_at = db.Column(db.DateTime, default=func.now())
    feedback = db.Column(db.Text())
    response_status = db.Column(db.Text(), default="pending")


class SystemPrompt(db.Model):
    __tablename__ = "prompts_history"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    type = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class ChatError(db.Model):
    __tablename__ = "error_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id))
    user_input = db.Column(db.Text())
    error_type = db.Column(db.Text())
    error_details = db.Column(db.Text())
    version = db.Column(db.Text(), default=None, nullable=True)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime(), default=func.now())
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text(), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class UserFiles(db.Model):
    __tablename__ = "user_files"
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.Text())
    s3_url = db.Column(db.Text())
    embedded = db.Column(db.Boolean, default=False)
    hash = db.Column(db.Text(), default=None, nullable=True)
    error_info = db.Column(db.Text(), default=None, nullable=True)
    password = db.Column(db.Text(), default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class EvaluationScores(db.Model):
    __tablename__ = "evaluation_scores"
    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey("chatbot_datas.id"))
    user_input = db.Column(db.Text(), nullable=False)
    final_response = db.Column(db.Text(), nullable=False)
    feedback = db.Column(db.Text())
    faithfulness = db.Column(db.Float)
    answer_relevancy = db.Column(db.Float)
    context_utilization = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class ChatbotMetrics(db.Model):
    __tablename__ = "chatbot_metrics"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user_id))
    exchange_count = db.Column(db.Integer)
    exchange_ids = db.Column(db.Text())
    response_accepted_count = db.Column(db.Integer)
    response_declined_count = db.Column(db.Integer)
    response_time = db.Column(db.SmallInteger)
    exchange_cost = db.Column(db.Numeric(5, 3))
    time_stamp = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


class Conversation(db.Model):
    __tablename__ = "conversation"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    uuid = db.Column(db.Text, unique=True, nullable=True)
    collection_name = db.Column(db.Text())
    time_stamp = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
