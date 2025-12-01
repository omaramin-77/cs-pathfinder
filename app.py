import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db_connection
from ai_helper import choose_field_from_answers
from roadmaps_data import ROADMAPS
from datetime import datetime

app = Flask(__name__)
app.secret_key = '12345' #need to chnge later

init_db()

@app.route('/')
def home():
    return render_template('home.html', email=session.get('email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)',
                        (email, password_hash))
            conn.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email already registered. Please log in.', 'error')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))



@app.route("/quiz/<int:id>", methods=["GET", "POST"]) 
def quiz_question(id: int):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'answers' not in session:
        session['answers'] = {}
    
    if request.method == "POST":
        answer = request.form.get("answer")

        conn = get_db_connection()
        qrow = conn.execute('SELECT question_text FROM quiz_questions WHERE id = ?', (id,)).fetchone()
        conn.close()


        question_text = qrow['question_text'] if qrow and 'question_text' in qrow.keys() else ''
        
        session['answers'][str(id)] = {
            'question': question_text,
            'answer': answer
        }
        session.modified = True
        
        conn = get_db_connection()
        next_question = conn.execute('SELECT id FROM quiz_questions WHERE id > ? ORDER BY id LIMIT 1', 
                                     (id,)).fetchone()
        conn.close()
        
        if next_question:
            return redirect(url_for('quiz_question', id=next_question['id']))
        else:
            return redirect(url_for('quiz_complete'))
    
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM quiz_questions WHERE id = ?', (id,)).fetchone()
    total_questions = conn.execute('SELECT COUNT(*) as count FROM quiz_questions').fetchone()['count']
    conn.close()
    
    if not question:
        flash('Question not found!', 'error')
        return redirect(url_for('home'))
    
    return render_template('quiz_question.html', 
                          question=question, 
                          question_num=id,
                          total=total_questions)


@app.route("/quiz/complete")
def quiz_complete():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if "answers" not in session or len(session['answers']) == 0:
        flash("Please complete the quiz first", "error")
        return redirect(url_for("home"))
    
    return render_template('quiz_complete.html', answers=session['answers'])

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    answers = session.get("answers", {})
    if not answers:
        flash("No answers found", "error")
        return redirect(url_for("home"))

    field_name = choose_field_from_answers(answers)

    conn = get_db_connection()
    conn.execute('INSERT INTO user_fields (user_id, field_name, timestamp) VALUES (?, ?, ?)',
                (session['user_id'], field_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    

    session.pop('answers', None)
    
    flash(f'Your recommended field: {field_name}!', 'success')
    return redirect(url_for('results'))




@app.route("/results")
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
     
    conn = get_db_connection()
    fields = conn.execute('SELECT * FROM user_fields WHERE user_id = ? ORDER BY timestamp DESC',
                         (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template("results.html", fields=results)

@app.route("/remove_field/<int:id>", methods=["POST"])
def remove_field(id: int):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM user_fields WHERE id = ? AND user_id = ?',
                (id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash("Field removed", "success")
    return redirect(url_for("results"))

@app.route("/roadmap/<field>")
def roadmap(field: str):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if field not in ROADMAPS:
        flash('Roadmap not found!', 'error')
        return redirect(url_for('results'))
    
    steps = ROADMAPS[field]
    
    conn = get_db_connection()
    progress_rows = conn.execute(
        'SELECT step_number, completed FROM roadmap_progress WHERE user_id = ? AND field_name = ?',
        (session['user_id'], field)
    ).fetchall()
    conn.close()
    
    progress = {row['step_number']: row['completed'] for row in progress_rows}
    
    total_steps = len(steps)
    completed_steps = sum(1 for p in progress.values() if p == 1)
    percentage = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0
    
    return render_template("roadmap.html", field=field
                          steps=steps,
                          progress=progress,
                          percentage=percentage,
                          total_steps=total_steps,
                          completed_steps=completed_steps)

@app.route("/roadmap/<field>/update", methods=["POST"])
def update_roadmap(field: str):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    step_number = int(request.form.get('step_number'))
    completed = int(request.form.get('completed'))
    
    conn = get_db_connection()
    
    existing = conn.execute(
        'SELECT id FROM roadmap_progress WHERE user_id = ? AND field_name = ? AND step_number = ?',
        (session['user_id'], field, step_number)
    ).fetchone()
    
    if existing:
        conn.execute(
            'UPDATE roadmap_progress SET completed = ? WHERE user_id = ? AND field_name = ? AND step_number = ?',
            (completed, session['user_id'], field, step_number)
        )
    else:
        conn.execute(
            'INSERT INTO roadmap_progress (user_id, field_name, step_number, completed) VALUES (?, ?, ?, ?)',
            (session['user_id'], field, step_number, completed)
        )
    
    conn.commit()
    conn.close()
    
    return redirect(url_for("roadmap", field=field))

@app.route("/roadmap/<field>/reset", methods=["POST"])
def reset_roadmap(field: str):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM roadmap_progress WHERE user_id = ? AND field_name = ?',
                (session['user_id'], field))
    conn.commit()
    conn.close()
    flash("Progress reset", "success")
    return redirect(url_for("roadmap", field=field))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)