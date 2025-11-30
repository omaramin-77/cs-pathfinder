import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '12345' #need to chnge later

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'password':
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # save to databasee
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



@app.route("/quiz/<int:id>", methods=["GET", "POST"]) 
def quiz_question(id: int):
    
    if request.method == "POST":
        
        answers = session.get("answers", {})
        answer = request.form.get("answer")
        question_text = request.form.get("question_text", "")
        answers[str(id)] = {"question": question_text, "answer": answer}
        session["answers"] = answers
        
        max_questions = 20  
        if id > max_questions:
            return redirect(url_for("quiz_complete"))
        return redirect(url_for("quiz_question", id=id + 1))


if __name__ == '__main__':
    app.run(debug=True)