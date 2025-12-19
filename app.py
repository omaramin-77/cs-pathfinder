import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from DB import init_db, get_db_connection
from ai_helper import choose_field_from_answers
from BlogScraping import (refresh_rss_feed, get_all_blogs, get_blog_by_id, 
                          update_blog, delete_blog, get_blogs_paginated)
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from api_ranker import APICVRanker

app = Flask(__name__)
app.secret_key = '12345'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'pdf_cvs'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

# ============ ADMIN DECORATOR ============

def admin_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user or user['is_admin'] != 1:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('home.html', email=session.get('email'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            
            # Redirect admins to dashboard
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
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
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)',
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
        cursor = conn.cursor()
        cursor.execute('SELECT question_text FROM quiz_questions WHERE id = ?', (id,))
        qrow = cursor.fetchone()
        conn.close()

        question_text = qrow['question_text'] if qrow else ''
        
        session['answers'][str(id)] = {
            'question': question_text,
            'answer': answer
        }
        session.modified = True
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM quiz_questions WHERE id > ? ORDER BY id LIMIT 1', (id,))
        next_question = cursor.fetchone()
        conn.close()
        
        if next_question:
            return redirect(url_for('quiz_question', id=next_question['id']))
        else:
            return redirect(url_for('quiz_complete'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quiz_questions WHERE id = ?', (id,))
    question = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) as count FROM quiz_questions')
    total_questions = cursor.fetchone()['count']
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
    cursor = conn.cursor()

    # ✅ Prevent duplication
    cursor.execute(
        'SELECT 1 FROM user_fields WHERE user_id = ? AND field_name = ?',
        (session['user_id'], field_name)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO user_fields (user_id, field_name, timestamp) VALUES (?, ?, ?)',
            (session['user_id'], field_name, datetime.now().isoformat())
        )
        conn.commit()
    else:
        flash(f'Field "{field_name}" already exists in your results.', 'error')

    conn.close()

    session.pop('answers', None)
    flash(f'Your recommended field: {field_name}!', 'success')
    return redirect(url_for('results'))

@app.route("/results")
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
     
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_fields WHERE user_id = ? ORDER BY timestamp DESC', (session['user_id'],))
    fields = cursor.fetchall()
    conn.close()
    
    return render_template("results.html", fields=fields)

@app.route("/remove_field/<int:id>", methods=["POST"])
def remove_field(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_fields WHERE id = ? AND user_id = ?',
                (id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash("Field removed", "success")
    return redirect(url_for("results"))

@app.route("/roadmap/<field>")
def roadmap(field):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM roadmaps WHERE field_name = ?', (field,))
    roadmap = cursor.fetchone()
    if not roadmap:
        conn.close()
        flash('Roadmap not found!', 'error')
        return redirect(url_for('results'))
    
    cursor.execute('''
        SELECT step_number, step_text as text, description, course_url as course 
        FROM roadmap_steps WHERE roadmap_id = ? ORDER BY step_number
    ''', (roadmap['id'],))
    steps = cursor.fetchall()
    
    cursor.execute(
        'SELECT step_number, completed FROM roadmap_progress WHERE user_id = ? AND field_name = ?',
        (session['user_id'], field)
    )
    progress = {row['step_number']: row['completed'] for row in cursor.fetchall()}
    conn.close()
    
    total_steps = len(steps)
    completed_steps = sum(1 for p in progress.values() if p == 1)
    percentage = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0
    
    return render_template('roadmap.html', field=field, steps=steps, progress=progress,
                          percentage=percentage, total_steps=total_steps, completed_steps=completed_steps)

@app.route("/roadmap/<field>/update", methods=["POST"])
def update_roadmap(field):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    step_number = int(request.form.get('step_number'))
    completed = int(request.form.get('completed'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM roadmap_progress WHERE user_id = ? AND field_name = ? AND step_number = ?',
        (session['user_id'], field, step_number)
    )
    
    if cursor.fetchone():
        cursor.execute(
            'UPDATE roadmap_progress SET completed = ? WHERE user_id = ? AND field_name = ? AND step_number = ?',
            (completed, session['user_id'], field, step_number)
        )
    else:
        cursor.execute(
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
    cursor = conn.cursor()
    cursor.execute('DELETE FROM roadmap_progress WHERE user_id = ? AND field_name = ?',
                (session['user_id'], field))
    conn.commit()
    conn.close()
    flash("Progress reset", "success")
    return redirect(url_for("roadmap", field=field))


@app.route('/cv-ranker')
def cv_ranker():
    """CV Ranker landing page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM job_descriptions ORDER BY title')
    job_descriptions = cursor.fetchall()
    cursor.execute('''
        SELECT * FROM cv_rankings 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    ''', (session['user_id'],))
    rankings = cursor.fetchall()
    conn.close()
    
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
    """Retrieve job description based on type"""
    if job_desc_type == 'predefined':
        job_desc_id = request.form.get('job_desc_id')
        if not job_desc_id:
            return None, None, 'Please select a job description'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT description FROM job_descriptions WHERE id = ?', (job_desc_id,))
        job_desc_row = cursor.fetchone()
        conn.close()
        
        if not job_desc_row:
            return None, None, 'Job description not found'
        
        return job_desc_row['description'], job_desc_id, None
    else:
        job_description = request.form.get('custom_job_desc', '').strip()
        if not job_description:
            return None, None, 'Please provide a job description'
        return job_description, None, None


def _save_ranking_result(cv_filename, job_desc_id, job_description, job_desc_type, result):
    """Save CV ranking result to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cv_rankings 
        (user_id, cv_filename, job_description_id, custom_job_description, 
         overall_score, matching_analysis, description, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'],
        secure_filename(cv_filename),
        job_desc_id if job_desc_type == 'predefined' else None,
        job_description if job_desc_type == 'custom' else None,
        result.get('overall_score', 0),
        result.get('matching_analysis', ''),
        result.get('description', ''),
        result.get('recommendation', '')
    ))
    conn.commit()
    ranking_id = cursor.lastrowid
    conn.close()
    return ranking_id


@app.route('/cv-ranker/rank', methods=['POST'])
def rank_cv():
    """Rank uploaded CV against job description"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Validate CV file
    if 'cv_file' not in request.files:
        flash('No CV file uploaded', 'error')
        return redirect(url_for('cv_ranker'))
    
    cv_file = request.files['cv_file']
    is_valid, error_msg = _validate_cv_file(cv_file)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('cv_ranker'))
    
    # Get job description
    job_desc_type = request.form.get('job_desc_type')
    job_description, job_desc_id, error_msg = _get_job_description(job_desc_type)
    if error_msg:
        flash(error_msg, 'error')
        return redirect(url_for('cv_ranker'))
    
    # Rank CV
    try:
        ranker = APICVRanker()
        result = ranker.rank_single_cv(job_description, cv_file)
        
        if 'error' in result:
            flash(f'Error ranking CV: {result["error"]}', 'error')
            return redirect(url_for('cv_ranker'))
        
        # Save result
        ranking_id = _save_ranking_result(
            cv_file.filename, job_desc_id, job_description, job_desc_type, result
        )
        
        flash('CV ranked successfully!', 'success')
        return redirect(url_for('cv_ranking_result', ranking_id=ranking_id))
        
    except Exception as e:
        flash(f'Error processing CV: {str(e)}', 'error')
        return redirect(url_for('cv_ranker'))

@app.route('/cv-ranker/result/<int:ranking_id>')
def cv_ranking_result(ranking_id):
    """Display CV ranking result"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, j.title as job_title 
        FROM cv_rankings r
        LEFT JOIN job_descriptions j ON r.job_description_id = j.id
        WHERE r.id = ? AND r.user_id = ?
    ''', (ranking_id, session['user_id']))
    ranking = cursor.fetchone()
    conn.close()
    
    if not ranking:
        flash('Ranking not found', 'error')
        return redirect(url_for('cv_ranker'))
    
    return render_template('cv_ranking_result.html', ranking=ranking)

@app.route('/cv-ranker/history')
def cv_ranking_history():
    """View all CV ranking history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, j.title as job_title 
        FROM cv_rankings r
        LEFT JOIN job_descriptions j ON r.job_description_id = j.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    rankings = cursor.fetchall()
    conn.close()
    
    return render_template('cv_ranking_history.html', rankings=rankings)

@app.route('/cv-ranker/delete/<int:ranking_id>', methods=['POST'])
def delete_cv_ranking(ranking_id):
    """Delete a CV ranking"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cv_rankings WHERE id = ? AND user_id = ?', 
                (ranking_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Ranking deleted', 'success')
    return redirect(url_for('cv_ranking_history'))


@app.route('/news')
def news_list():
    """Display blog posts with pagination"""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    per_page = 8
    result = get_blogs_paginated(page=page, per_page=per_page)
    total = result['total']
    blogs = result['blogs']
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template('news.html', blogs=blogs, page=page, total_pages=total_pages)

@app.route('/news/<int:blog_id>')
def news_detail(blog_id):
    """Display single blog post"""
    blog = get_blog_by_id(blog_id)
    if not blog:
        flash('Blog post not found', 'error')
        return redirect(url_for('news_list'))
    # Prefer full_html when available
    return render_template('news_detail.html', blog=blog)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard homepage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    user_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM quiz_questions')
    question_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM blogs')
    blog_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM job_descriptions')
    job_desc_count = cursor.fetchone()['count']
    conn.close()
    
    return render_template('admin/dashboard.html', 
                          user_count=user_count,
                          question_count=question_count,
                          blog_count=blog_count,
                          job_desc_count=job_desc_count)

@app.route('/admin/users')
@admin_required
def admin_users():
    """View all users and manage admin status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, is_admin FROM users ORDER BY id DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@admin_required
def admin_new_user():
    """Create a new user"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('admin_new_user'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('admin_new_user'))
        
        password_hash = generate_password_hash(password)
        # Check if admin checkbox was checked (value="1" or exists in form)
        admin_status = 1 if is_admin in ('1', 'on', True) else 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (email, password_hash, is_admin) VALUES (?, ?, ?)',
                (email, password_hash, admin_status)
            )
            conn.commit()
            flash(f'User {email} created successfully!', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('admin_new_user'))
    
    return render_template('admin/user_form.html')

@app.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    """Toggle admin status for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        new_status = 1 - user['is_admin']
        cursor.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        status_text = 'promoted to admin' if new_status else 'demoted from admin'
        flash(f'User {status_text}', 'success')
    
    conn.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and their data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete associated data first
        cursor.execute('DELETE FROM roadmap_progress WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM user_fields WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/questions')
@admin_required
def admin_questions():
    """View all quiz questions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quiz_questions ORDER BY id')
    questions = cursor.fetchall()
    conn.close()
    return render_template('admin/questions.html', questions=questions)

@app.route('/admin/questions/new', methods=['GET', 'POST'])
@admin_required
def admin_new_question():
    """Create a new quiz question"""
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        
        if not all([question_text, option_a, option_b, option_c, option_d]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_new_question'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO quiz_questions (question_text, option_a, option_b, option_c, option_d)
                VALUES (?, ?, ?, ?, ?)
            ''', (question_text, option_a, option_b, option_c, option_d))
            conn.commit()
            flash('Question created successfully', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'Error creating question: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('admin/question_form.html')

@app.route('/admin/questions/<int:q_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_question(q_id):
    """Edit an existing quiz question"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quiz_questions WHERE id = ?', (q_id,))
    question = cursor.fetchone()
    
    if not question:
        flash('Question not found', 'error')
        conn.close()
        return redirect(url_for('admin_questions'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        
        if not all([question_text, option_a, option_b, option_c, option_d]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_edit_question', q_id=q_id))
        
        try:
            cursor.execute('''
                UPDATE quiz_questions 
                SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?
                WHERE id = ?
            ''', (question_text, option_a, option_b, option_c, option_d, q_id))
            conn.commit()
            flash('Question updated successfully', 'success')
            conn.close()
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'Error updating question: {str(e)}', 'error')
            conn.close()
            return redirect(url_for('admin_edit_question', q_id=q_id))
    
    conn.close()
    return render_template('admin/question_form.html', question=question, edit=True)

@app.route('/admin/questions/<int:q_id>/delete', methods=['POST'])
@admin_required
def delete_question(q_id):
    """Delete a quiz question"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM quiz_questions WHERE id = ?', (q_id,))
        conn.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_questions'))

@app.route('/admin/roadmaps')
@admin_required
def admin_roadmaps():
    """View all roadmaps"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT field_name FROM roadmaps ORDER BY field_name')
    roadmaps = cursor.fetchall()
    conn.close()
    roadmap_names = [r['field_name'] for r in roadmaps]
    return render_template('admin/roadmap_list.html', roadmaps=roadmap_names)

@app.route('/admin/roadmaps/new', methods=['GET', 'POST'])
@admin_required
def admin_new_roadmap():
    """Create a new roadmap"""
    if request.method == 'POST':
        field_name = request.form.get('field_name', '').strip()
        
        if not field_name:
            flash('Field name is required', 'error')
            return redirect(url_for('admin_new_roadmap'))
        
        # Check if roadmap already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM roadmaps WHERE field_name = ?', (field_name,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            flash(f'Roadmap for "{field_name}" already exists', 'error')
            return redirect(url_for('admin_new_roadmap'))
        
        try:
            cursor.execute('INSERT INTO roadmaps (field_name) VALUES (?)', (field_name,))
            conn.commit()
            roadmap_id = cursor.lastrowid
            conn.close()
            
            flash(f'Roadmap "{field_name}" created successfully! You can now add steps.', 'success')
            return redirect(url_for('admin_edit_roadmap', field=field_name))
        except Exception as e:
            conn.close()
            flash(f'Error creating roadmap: {str(e)}', 'error')
            return redirect(url_for('admin_new_roadmap'))
    
    return render_template('admin/roadmap_form.html')

@app.route('/admin/roadmaps/<field>/delete', methods=['POST'])
@admin_required
def admin_delete_roadmap(field):
    """Delete a roadmap and all its steps"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get roadmap ID
        cursor.execute('SELECT id FROM roadmaps WHERE field_name = ?', (field,))
        roadmap = cursor.fetchone()
        
        if not roadmap:
            conn.close()
            flash('Roadmap not found', 'error')
            return redirect(url_for('admin_roadmaps'))
        
        roadmap_id = roadmap['id']
        
        # Delete all steps first (foreign key constraint)
        cursor.execute('DELETE FROM roadmap_steps WHERE roadmap_id = ?', (roadmap_id,))
        
        # Delete the roadmap
        cursor.execute('DELETE FROM roadmaps WHERE id = ?', (roadmap_id,))
        
        conn.commit()
        conn.close()
        
        flash(f'Roadmap "{field}" deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting roadmap: {str(e)}', 'error')
    
    return redirect(url_for('admin_roadmaps'))

@app.route('/admin/roadmaps/<field>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_roadmap(field):
    """Edit roadmap content"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM roadmaps WHERE field_name = ?', (field,))
    roadmap = cursor.fetchone()
    
    if not roadmap:
        conn.close()
        flash('Roadmap not found', 'error')
        return redirect(url_for('admin_roadmaps'))
    
    cursor.execute('''
        SELECT id, step_number, step_text as text, description, course_url as course 
        FROM roadmap_steps 
        WHERE roadmap_id = ? 
        ORDER BY step_number
    ''', (roadmap['id'],))
    steps = cursor.fetchall()
    conn.close()
    
    return render_template('admin/roadmap_edit.html', field=field, steps=steps, roadmap_id=roadmap['id'])

@app.route('/admin/roadmaps/<int:roadmap_id>/steps/add', methods=['POST'])
@admin_required
def admin_add_roadmap_step(roadmap_id):
    """Add a new step to a roadmap"""
    step_text = request.form.get('step_text', '').strip()
    description = request.form.get('description', '').strip()
    course_url = request.form.get('course_url', '').strip()
    
    if not step_text:
        flash('Step text is required', 'error')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT field_name FROM roadmaps WHERE id = ?', (roadmap_id,))
        roadmap = cursor.fetchone()
        conn.close()
        return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get next step number
        cursor.execute(
            'SELECT MAX(step_number) as max_step FROM roadmap_steps WHERE roadmap_id = ?', 
            (roadmap_id,)
        )
        result = cursor.fetchone()
        max_step = result['max_step'] or 0
        
        cursor.execute('''
            INSERT INTO roadmap_steps (roadmap_id, step_number, step_text, description, course_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (roadmap_id, max_step + 1, step_text, description, course_url))
        conn.commit()
        
        cursor.execute('SELECT field_name FROM roadmaps WHERE id = ?', (roadmap_id,))
        roadmap = cursor.fetchone()
        conn.close()
        
        flash('Step added successfully', 'success')
        return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))
    except Exception as e:
        flash(f'Error adding step: {str(e)}', 'error')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT field_name FROM roadmaps WHERE id = ?', (roadmap_id,))
        roadmap = cursor.fetchone()
        conn.close()
        return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))

@app.route('/admin/roadmaps/steps/<int:step_id>/edit', methods=['POST'])
@admin_required
def admin_edit_roadmap_step(step_id):
    """Edit a roadmap step"""
    step_text = request.form.get('step_text', '').strip()
    description = request.form.get('description', '').strip()
    course_url = request.form.get('course_url', '').strip()
    
    if not step_text:
        flash('Step text is required', 'error')
        return redirect(request.referrer or url_for('admin_roadmaps'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT roadmap_id FROM roadmap_steps WHERE id = ?', (step_id,))
        step = cursor.fetchone()
        
        if not step:
            conn.close()
            flash('Step not found', 'error')
            return redirect(url_for('admin_roadmaps'))
        
        cursor.execute('''
            UPDATE roadmap_steps 
            SET step_text = ?, description = ?, course_url = ?
            WHERE id = ?
        ''', (step_text, description, course_url, step_id))
        conn.commit()
        
        cursor.execute('SELECT field_name FROM roadmaps WHERE id = ?', (step['roadmap_id'],))
        roadmap = cursor.fetchone()
        conn.close()
        
        flash('Step updated successfully', 'success')
        return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))
    except Exception as e:
        flash(f'Error updating step: {str(e)}', 'error')
        return redirect(request.referrer or url_for('admin_roadmaps'))

@app.route('/admin/roadmaps/steps/<int:step_id>/delete', methods=['POST'])
@admin_required
def admin_delete_roadmap_step(step_id):
    """Delete a roadmap step"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT roadmap_id FROM roadmap_steps WHERE id = ?', (step_id,))
        step = cursor.fetchone()
        
        if not step:
            conn.close()
            flash('Step not found', 'error')
            return redirect(url_for('admin_roadmaps'))
        
        cursor.execute('DELETE FROM roadmap_steps WHERE id = ?', (step_id,))
        conn.commit()
        
        cursor.execute('SELECT field_name FROM roadmaps WHERE id = ?', (step['roadmap_id'],))
        roadmap = cursor.fetchone()
        conn.close()
        
        flash('Step deleted successfully', 'success')
        return redirect(url_for('admin_edit_roadmap', field=roadmap['field_name']))
    except Exception as e:
        flash(f'Error deleting step: {str(e)}', 'error')
        return redirect(request.referrer or url_for('admin_roadmaps'))

@app.route('/admin/blogs')
@admin_required
def admin_blogs():
    """View and manage blog posts"""
    blogs = get_all_blogs()
    return render_template('admin/blog_list.html', blogs=blogs)

@app.route('/admin/blogs/<int:blog_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_blog(blog_id):
    """Edit a blog post"""
    blog = get_blog_by_id(blog_id)
    
    if not blog:
        flash('Blog post not found', 'error')
        return redirect(url_for('admin_blogs'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        summary = request.form.get('summary')
        image_url = request.form.get('image_url')
        author = request.form.get('author')
        full_text = request.form.get('full_text')
        published_date = request.form.get('published_date')
        thumbnail = request.form.get('thumbnail')
        
        if not title or not summary:
            flash('Title and summary are required', 'error')
            return redirect(url_for('admin_edit_blog', blog_id=blog_id))
        
        if update_blog(blog_id, title=title, summary=summary, image_url=image_url,
                       author=author, full_text=full_text, thumbnail=thumbnail,
                       published_date=published_date):
            flash('Blog post updated successfully', 'success')
            return redirect(url_for('admin_blogs'))
        else:
            flash('Error updating blog post', 'error')
    
    return render_template('admin/edit_blog.html', blog=blog)

@app.route('/admin/blogs/<int:blog_id>/delete', methods=['POST'])
@admin_required
def admin_delete_blog(blog_id):
    """Delete a blog post"""
    if delete_blog(blog_id):
        flash('Blog post deleted successfully', 'success')
    else:
        flash('Error deleting blog post', 'error')
    
    return redirect(url_for('admin_blogs'))

@app.route('/admin/blogs/refresh', methods=['POST'])
@admin_required
def admin_refresh_blogs():
    """Refresh RSS feed and fetch new articles"""
    result = refresh_rss_feed()
    
    if result['success']:
        flash(f"Feed refreshed! {result['new_count']} new articles added. Total: {result['total_count']}", 'success')
    else:
        flash(f"Feed refresh failed: {result['message']}", 'error')
    
    return redirect(url_for('admin_blogs'))

@app.route('/admin/job-descriptions')
@admin_required
def admin_job_descriptions():
    """View all job descriptions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT j.*, u.email as creator_email 
        FROM job_descriptions j
        JOIN users u ON j.created_by = u.id
        ORDER BY j.created_at DESC
    ''')
    job_descriptions = cursor.fetchall()
    conn.close()
    return render_template('admin/job_descriptions.html', job_descriptions=job_descriptions)

@app.route('/admin/job-descriptions/new', methods=['GET', 'POST'])
@admin_required
def admin_new_job_description():
    """Create a new job description"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title or not description:
            flash('Title and description are required', 'error')
            return redirect(url_for('admin_new_job_description'))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_descriptions (title, description, created_by)
                VALUES (?, ?, ?)
            ''', (title, description, session['user_id']))
            conn.commit()
            conn.close()
            
            flash('Job description created successfully', 'success')
            return redirect(url_for('admin_job_descriptions'))
        except Exception as e:
            flash(f'Error creating job description: {str(e)}', 'error')
    
    return render_template('admin/job_description_form.html')

@app.route('/admin/job-descriptions/<int:job_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_job_description(job_id):
    """Edit a job description"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM job_descriptions WHERE id = ?', (job_id,))
    job_desc = cursor.fetchone()
    
    if not job_desc:
        conn.close()
        flash('Job description not found', 'error')
        return redirect(url_for('admin_job_descriptions'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title or not description:
            flash('Title and description are required', 'error')
            return redirect(url_for('admin_edit_job_description', job_id=job_id))
        
        try:
            cursor.execute('''
                UPDATE job_descriptions 
                SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, description, job_id))
            conn.commit()
            conn.close()
            
            flash('Job description updated successfully', 'success')
            return redirect(url_for('admin_job_descriptions'))
        except Exception as e:
            conn.close()
            flash(f'Error updating job description: {str(e)}', 'error')
    
    conn.close()
    return render_template('admin/job_description_form.html', job_desc=job_desc, edit=True)

@app.route('/admin/job-descriptions/<int:job_id>/delete', methods=['POST'])
@admin_required
def admin_delete_job_description(job_id):
    """Delete a job description"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM job_descriptions WHERE id = ?', (job_id,))
        conn.commit()
        conn.close()
        flash('Job description deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting job description: {str(e)}', 'error')
    
    return redirect(url_for('admin_job_descriptions'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
