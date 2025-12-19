import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from DB import init_db, get_db_connection
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
def quiz_question(id):
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
    
    return render_template("results.html", fields=fields)

@app.route("/remove_field/<int:id>", methods=["POST"])
def remove_field(id):
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
def roadmap(field):
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
    
    return render_template('roadmap.html', field=field,
                          steps=steps,
                          progress=progress,
                          percentage=percentage,
                          total_steps=total_steps,
                          completed_steps=completed_steps)

@app.route("/roadmap/<field>/update", methods=["POST"])
def update_roadmap(field):
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
def reset_roadmap(field):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM roadmap_progress WHERE user_id = ? AND field_name = ?',
                (session['user_id'], field))
    conn.commit()
    conn.close()
    flash("Progress reset", "success")
    return redirect(url_for("roadmap", field=field))



@app.route('/cv-ranker')
def cv_ranker():
    return render_template('cv_ranker.html', 
                          job_descriptions=job_descriptions,
                          rankings=rankings)


def _validate_cv_file(cv_file):
    """Validate uploaded CV file"""
    if not cv_file or cv_file.filename == '':
        return False, 'No file selected'
    if not cv_file.filename.lower().endswith('.pdf'):
        return False, 'Only PDF files are allowed'
    return True, None


def _get_job_description(job_desc_type):
    return job_description

def _save_ranking_result(cv_filename, job_desc_id, job_description):
    return ranking_id


@app.route('/cv-ranker/rank', methods=['POST'])
def rank_cv():
    flash('CV ranked successfully!', 'success')
    return redirect(url_for('cv_ranking_result', ranking_id=ranking_id))

@app.route('/cv-ranker/result/<int:ranking_id>')
def cv_ranking_result(ranking_id):
    return render_template('cv_ranking_result.html', ranking=ranking)


@app.route('/cv-ranker/history')
def cv_ranking_history():
    return render_template('cv_ranking_history.html', rankings=rankings)


@app.route('/cv-ranker/delete/<int:ranking_id>', methods=['POST'])
def delete_cv_ranking(ranking_id):
    flash('Ranking deleted', 'success')
    return redirect(url_for('cv_ranking_history'))

@app.route('/news')
def news_list():
    return render_template('news_list.html', articles=news_articles)


@app.route('/news/<int:blog_id>')
def news_detail(blog_id):
    return render_template('news_detail.html', blog=blog)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@admin_required
def admin_new_user():
    if request.method == 'POST':
        flash('New user created', 'success')
        return render_template('admin_new_user.html')


@app.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    flash('User admin status toggled', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    flash('User deleted', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/questions')
@admin_required
def admin_questions():
    return render_template('admin_questions.html', questions=questions)


@app.route('/admin/questions/new', methods=['GET', 'POST'])
@admin_required
def admin_new_question():
    if request.method == 'POST':
        flash('New question added', 'success')
        return redirect(url_for('admin_questions'))
    return render_template('admin_new_question.html')

@app.route('/admin/questions/<int:q_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_question(q_id):
    return render_template('admin/question_form.html', question=question, edit=True)


@app.route('/admin/questions/<int:q_id>/delete', methods=['POST'])
@admin_required
def delete_question(q_id):
    flash('Question deleted', 'success')
    return redirect(url_for('admin_questions'))

@app.route('/admin/roadmaps')
@admin_required
def admin_roadmaps():
    return render_template('admin_roadmaps.html', roadmaps=roadmaps)

@app.route('/admin/roadmaps/new', methods=['GET', 'POST'])
@admin_required
def admin_new_roadmap():
    if request.method == 'POST':
        flash('New roadmap created', 'success')
        return redirect(url_for('admin_roadmaps'))
    

@app.route('/admin/roadmaps/<field>/delete', methods=['POST'])
@admin_required
def admin_delete_roadmap(field):
    flash('Roadmap deleted', 'success')
    return redirect(url_for('admin_roadmaps'))


@app.route('/admin/roadmaps/<field>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_roadmap(field):
    return render_template('admin/roadmap_edit.html', field=field, steps=steps, roadmap_id=roadmap['id'])


@app.route('/admin/roadmaps/<int:roadmap_id>/steps/add', methods=['POST'])
@admin_required
def admin_add_roadmap_step(roadmap_id):
    return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))


@app.route('/admin/roadmaps/steps/<int:step_id>/edit', methods=['POST'])
@admin_required
def admin_edit_roadmap_step(step_id):
    return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))


@app.route('/admin/roadmaps/steps/<int:step_id>/delete', methods=['POST'])
@admin_required
def admin_delete_roadmap_step(step_id):
    return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))


@app.route('/admin/blogs')
@admin_required
def admin_blogs():
    return render_template('admin_blogs.html', blogs=blogs)


@app.route('/admin/blogs/<int:blog_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_blog(blog_id):
    return render_template('admin/edit_blog.html', blog=blog)


@app.route('/admin/blogs/<int:blog_id>/delete', methods=['POST'])
@admin_required
def admin_delete_blog(blog_id):    
    return redirect(url_for('admin_blogs'))

@app.route('/admin/job-descriptions')
@admin_required
def admin_job_descriptions():
    return render_template('admin_job_descriptions.html', job_descriptions=job_descriptions)


@app.route('/admin/job-descriptions/new', methods=['GET', 'POST'])
@admin_required
def admin_new_job_description():    
    return render_template('admin/job_description_form.html')


@app.route('/admin/job-descriptions/<int:job_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_job_description(job_id):
    return render_template('admin/job_description_form.html', job_description=job_description, edit=True)


@app.route('/admin/job-descriptions/<int:job_id>/delete', methods=['POST'])
@admin_required
def admin_delete_job_description(job_id):
    return redirect(url_for('admin_job_descriptions'))




if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)