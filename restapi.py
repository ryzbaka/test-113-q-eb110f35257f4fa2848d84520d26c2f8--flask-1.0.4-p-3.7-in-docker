from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import os
import pickle
app = Flask(__name__)
basedir=os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+os.path.join(basedir,'test.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False


db=SQLAlchemy(app)
ma=Marshmallow(app)


if not os.path.exists(os.path.join(basedir,"quiz_id.pickle")):
    with open("quiz_id.pickle",'wb') as f:
        quiz_id=0
        pickle.dump(quiz_id,f)#for quiz-tracking

if not os.path.exists(os.path.join(basedir,"ques_id.pickle")):
    with open("ques_id.pickle",'wb') as f:
        ques_id=0
        pickle.dump(ques_id,f)#for question-tracking


class Quiz(db.Model):
    __tablename__="quiz"
    id=db.Column(db.Integer,primary_key=True,autoincrement=False)
    name=db.Column(db.String(50))
    description=db.Column(db.String(100))

    def __init__(self,id,name,description):
        self.id=id
        self.name=name
        self.description=description

class QuizSchema(ma.Schema):
    class Meta:
        fields=["id","name","description"]
quiz_schema=QuizSchema()

class Question(db.Model):
    __tablename__="question"
    id=db.Column(db.Integer,primary_key=True,autoincrement=False)
    name=db.Column(db.String)
    options=db.Column(db.String)#comma separated values
    correct_option=db.Column(db.Integer)
    quiz=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    points=db.Column(db.Integer)

    def __init__(self,id,name,options,correct_option,quiz,points):
        self.id=id
        self.name=name
        self.options=options
        self.correct_option=correct_option
        self.quiz=quiz
        self.points=points

class QuestionSchema(ma.Schema):
    class Meta:
        fields=["id","name","options","correct_option","quiz","points"]

question_schema=QuestionSchema()
questions_schema=QuestionSchema(many=True)


if not os.path.exists(os.path.join(basedir,"initialized.pickle")):
    db.create_all()
    initialized=True
    with open("initialized.pickle",'wb') as f:
        pickle.dump(initialized,f)

@app.route("/")
def hello():
    return "Hello World!"
@app.route("/api/quiz/",methods=["POST"])
def add_quiz():#db.session.add.quiz
    with open("quiz_id.pickle",'rb') as f:
        quiz_id=pickle.load(f)
    name=request.json["name"]
    description=request.json["description"]
    newQuiz=Quiz(quiz_id,name,description)
    db.session.add(newQuiz)
    db.session.commit()
    with open("quiz_id.pickle",'wb')as f:
        quiz_id+=1
        pickle.dump(quiz_id,f)
    return quiz_schema.jsonify(newQuiz)

@app.route("/api/questions/",methods=["POST"])
def add_question():#db.session.add.quiz
    with open("ques_id.pickle",'rb') as f:
        ques_id=pickle.load(f)
    name=request.json["name"]
    options=request.json["options"]
    correct_option=request.json["correct_option"]
    quiz=request.json["quiz"]
    points=request.json["points"]
    newQuestion=Question(ques_id,name,options,correct_option,quiz,points)
    db.session.add(newQuestion)
    db.session.commit()
    with open("ques_id.pickle",'wb') as f:
        ques_id+=1
        pickle.dump(ques_id,f)
    return question_schema.jsonify(newQuestion)

@app.route("/api/question/<id>",methods=["GET"])
def get_question(id):
    question=Question.query.get(id)
    return question_schema.jsonify(question)

@app.route("/api/quiz-questions/<id>",methods=["GET"])
def get_quiz_details(id):
    quiz=Quiz.query.get(id)
    return quiz_schema.jsonify(quiz)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
