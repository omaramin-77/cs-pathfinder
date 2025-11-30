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


@app.route("/quiz/complete")
def quiz_complete():
    if "answers" not in session:
        flash("Please complete the quiz first", "error")
        return redirect(url_for("home"))
    return render_template('quiz_complete.html', answers=session['answers'])

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    answers = session.get("answers", {})
    if not answers:
        flash("No answers found", "error")
        return redirect(url_for("home"))

    #field_name = send_to_api(answers)

    session.pop('answers', None)
    
    flash(f'Your recommended field: {field_name}!', 'success')
    return redirect(url_for('results'))

@app.route("/results")
def results():
    results = session.get("results", [])
    return render_template("results.html", fields=results)

@app.route("/remove_field/<int:id>", methods=["POST"])
def remove_field(id: int):
    results = session.get("results", [])
    if 0 <= id < len(results):
        results.pop(id)
        session["results"] = results
        flash("Field removed", "success")
    return redirect(url_for("results"))

@app.route("/roadmap/<field>")
def roadmap(field: str):
    return render_template("roadmap.html", field=field)

@app.route("/roadmap/<field>/update", methods=["POST"])
def update_roadmap(field: str):
    flash("Roadmap updated (placeholder)", "success")
    return redirect(url_for("roadmap", field=field))

@app.route("/roadmap/<field>/reset", methods=["POST"])
def reset_roadmap(field: str):
    flash("Progress reset (placeholder)", "success")
    return redirect(url_for("roadmap", field=field))

if __name__ == '__main__':
    app.run(debug=True)