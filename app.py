import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '12345' #need to chnge later


def admin_required(f):
    return f




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
    app.run(debug=True)