
from flask import Flask
from werkzeug.utils import secure_filename
from Questgen import main
from question_generation.pipelines import pipeline
import PyPDF2 
import os
import re



UPLOAD_FOLDER = os.path.abspath(os.getcwd())


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
nlp = pipeline("question-generation")
answer = main.AnswerPredictor()

def GenerateQuestionAnswer(text):
    questions = []
    QuestionAnswer = {}
    
    
    text = text.replace("\n","")
    sentances = text.split(".")
    print(sentances)
    for sentance in sentances:
        if len(sentance) > 3:
            
            print(sentance)
            output = nlp(sentance)
    
            for item in output:
                questions.append(item['question'])


    print("question generated +++++++++++++++++++")
    for question in questions:
        payload3 = {
        "input_text" : text,
        "input_question" : question
    
        }
        output = answer.predict_answer(payload3)
        QuestionAnswer[question] = output

    return QuestionAnswer
  







@app.route('/HomePage' ,methods = ["GET","POST"])
def index():

    if (request.method == "GET"):
        return render_template("index.html")

    else:
        skip = []
        skipPages = request.form['pages']
        skipPages = skipPages.lower()

        if skipPages != "none":

            skip = skipPages.split(" ")
            
            for i,no in enumerate(skip):
                try:
                    skip[i] = int(no)
                except Exception:
                    continue
        
        if 'file' not in request.files:
            print("no file")
            return render_template("index.html")

        file = request.files['file']
        filename = secure_filename(file.filename)
        filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filePath)
        pdfFileObj = open(filePath, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        # printing number of pages in pdf file 
        maxPages = pdfReader.numPages

        
        
        
        data = {}
        for page in range(maxPages):
            #if page == 1:
                #break
            if page+1 in skip:
                
                continue
            
            pageObj = pdfReader.getPage(page)
            text = pageObj.extractText()
            text = re.sub('[^A-Za-z0-9]+', ' ', text)
            key = "Question & Answer for page no:"+str(page+1)

            data[key] = GenerateQuestionAnswer(text)
            #print(data)
            
        return render_template("table.html",result=data)





if __name__ == "__main__":
    app.run(debug = True)