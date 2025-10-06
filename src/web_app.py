# ============================================================================
# FILE: src/web_app.py
# ============================================================================
"""
Flask web application for Performance Evaluation System.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from datetime import timedelta
import logging
import sys
from pathlib import Path

# Add src directory to Python path if running from root
if __name__ == '__main__':
    src_path = Path(__file__).parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

import config
from file_store import FileStore
from auth import AuthManager
from models import User, Criterion, Evaluation, ValidationError
from business_logic import EvaluationEngine
from exports import ExcelExporter
from utils import setup_logging

# Initialize logging
setup_logging(config.LOGS_DIR)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=SESSION_LIFETIME_HOURS)

# Initialize stores
user_store = FileStore(USERS_FILE)
criteria_store = FileStore(CRITERIA_FILE)
evaluations_store = FileStore(EVALUATIONS_FILE)

# Initialize managers
auth_manager = AuthManager(user_store)
eval_engine = EvaluationEngine(criteria_store, evaluations_store)
exporter = ExcelExporter(EXPORTS_DIR)


# ============================================================================
# DECORATORS
# ============================================================================

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = user_store.find_by_id(session['user_id'])
            if not user or user.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# ROUTES - Authentication
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to dashboard or login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = auth_manager.authenticate(username, password)
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user.get('full_name', username)
            
            flash(f'Welcome back, {session["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# ROUTES - Dashboard
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    user = user_store.find_by_id(session['user_id'])
    role = user.get('role')
    
    context = {
        'user': user,
        'role': role
    }
    
    if role == ROLE_ADMIN:
        # Admin dashboard
        users = user_store.load()
        criteria = criteria_store.load()
        evaluations = evaluations_store.load()
        
        context.update({
            'total_users': len(users),
            'total_criteria': len(criteria),
            'total_evaluations': len(evaluations),
            'recent_evaluations': sorted(
                evaluations,
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )[:5]
        })
    
    elif role == ROLE_EVALUATOR:
        # Evaluator dashboard
        my_evaluations = evaluations_store.find_by(evaluator_id=session['user_id'])
        employees = user_store.find_by(role=ROLE_EMPLOYEE)
        
        context.update({
            'my_evaluations': len(my_evaluations),
            'total_employees': len(employees),
            'recent_evaluations': sorted(
                my_evaluations,
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )[:5]
        })
    
    elif role == ROLE_EMPLOYEE:
        # Employee dashboard
        my_evaluations = evaluations_store.find_by(employee_id=session['user_id'])
        summary = eval_engine.get_employee_summary(session['user_id'])
        
        context.update({
            'my_evaluations': my_evaluations,
            'summary': summary
        })
    
    return render_template('dashboard.html', **context)


# ============================================================================
# ROUTES - Users Management
# ============================================================================

@app.route('/users')
@role_required(ROLE_ADMIN)
def users_list():
    """List all users."""
    users = user_store.load()
    return render_template('users.html', users=users)


@app.route('/users/create', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def users_create():
    """Create new user."""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', '')
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validate using model
            User.create(username, password, role, full_name, email)
            
            # Create user
            user_id = auth_manager.create_user(username, password, role, full_name, email)
            
            if user_id:
                flash(f'User {username} created successfully!', 'success')
                return redirect(url_for('users_list'))
            else:
                flash('Failed to create user. Username may already exist.', 'danger')
        
        except ValidationError as e:
            flash(str(e), 'danger')
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash('An error occurred while creating the user.', 'danger')
    
    return render_template('users_create.html', roles=VALID_ROLES)


@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def users_edit(user_id):
    """Edit user details."""
    user = user_store.find_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users_list'))
    
    if request.method == 'POST':
        try:
            updates = {
                'full_name': request.form.get('full_name', '').strip(),
                'email': request.form.get('email', '').strip(),
                'role': request.form.get('role', ''),
                'active': request.form.get('active') == 'on'
            }
            
            if user_store.update(user_id, updates):
                flash('User updated successfully!', 'success')
                return redirect(url_for('users_list'))
            else:
                flash('Failed to update user.', 'danger')
        
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            flash('An error occurred while updating the user.', 'danger')
    
    return render_template('users_edit.html', user=user, roles=VALID_ROLES)


@app.route('/users/<user_id>/delete', methods=['POST'])
@role_required(ROLE_ADMIN)
def users_delete(user_id):
    """Delete user."""
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('users_list'))
    
    if user_store.delete(user_id):
        flash('User deleted successfully.', 'success')
    else:
        flash('Failed to delete user.', 'danger')
    
    return redirect(url_for('users_list'))


# ============================================================================
# ROUTES - Criteria Management
# ============================================================================

@app.route('/criteria')
@login_required
def criteria_list():
    """List all evaluation criteria."""
    criteria = criteria_store.load()
    return render_template('criteria.html', criteria=criteria)


@app.route('/criteria/create', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def criteria_create():
    """Create new criterion."""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            weight = float(request.form.get('weight', 1.0))
            description = request.form.get('description', '').strip()
            
            criterion = Criterion.create(name, weight, description)
            
            if criteria_store.create(criterion):
                flash(f'Criterion "{name}" created successfully!', 'success')
                return redirect(url_for('criteria_list'))
            else:
                flash('Failed to create criterion.', 'danger')
        
        except ValidationError as e:
            flash(str(e), 'danger')
        except ValueError:
            flash('Invalid weight value. Please enter a number.', 'danger')
        except Exception as e:
            logger.error(f"Error creating criterion: {e}")
            flash('An error occurred while creating the criterion.', 'danger')
    
    return render_template('criteria_create.html')


@app.route('/criteria/<criterion_id>/delete', methods=['POST'])
@role_required(ROLE_ADMIN)
def criteria_delete(criterion_id):
    """Delete criterion."""
    if criteria_store.delete(criterion_id):
        flash('Criterion deleted successfully.', 'success')
    else:
        flash('Failed to delete criterion.', 'danger')
    
    return redirect(url_for('criteria_list'))


# ============================================================================
# ROUTES - Evaluations
# ============================================================================

@app.route('/evaluations')
@login_required
def evaluations_list():
    """List evaluations based on role."""
    role = session.get('role')
    
    if role == ROLE_ADMIN:
        evaluations = evaluations_store.load()
    elif role == ROLE_EVALUATOR:
        evaluations = evaluations_store.find_by(evaluator_id=session['user_id'])
    else:  # ROLE_EMPLOYEE
        evaluations = evaluations_store.find_by(employee_id=session['user_id'])
    
    # Enrich with user names
    users_map = {u['id']: u.get('full_name', u['username']) for u in user_store.load()}
    criteria_map = eval_engine.get_criteria_map()
    
    for ev in evaluations:
        ev['employee_name'] = users_map.get(ev['employee_id'], 'Unknown')
        ev['evaluator_name'] = users_map.get(ev['evaluator_id'], 'Unknown')
        ev['weighted_score'] = eval_engine.compute_weighted_score(ev['scores'], criteria_map)
    
    return render_template('evaluations.html', evaluations=evaluations)


@app.route('/evaluations/create', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN, ROLE_EVALUATOR)
def evaluations_create():
    """Create new evaluation."""
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            comments = request.form.get('comments', '').strip()
            status = request.form.get('status', 'draft')
            
            # Collect scores
            scores = {}
            criteria = criteria_store.load()
            for criterion in criteria:
                score_value = request.form.get(f'score_{criterion["id"]}')
                if score_value:
                    scores[criterion['id']] = int(score_value)
            
            evaluation = Evaluation.create(
                employee_id=employee_id,
                evaluator_id=session['user_id'],
                scores=scores,
                comments=comments,
                status=status
            )
            
            if evaluations_store.create(evaluation):
                flash('Evaluation created successfully!', 'success')
                return redirect(url_for('evaluations_list'))
            else:
                flash('Failed to create evaluation.', 'danger')
        
        except ValidationError as e:
            flash(str(e), 'danger')
        except Exception as e:
            logger.error(f"Error creating evaluation: {e}")
            flash('An error occurred while creating the evaluation.', 'danger')
    
    # GET request
    employees = user_store.find_by(role=ROLE_EMPLOYEE)
    criteria = criteria_store.load()
    
    return render_template('evaluations_create.html', 
                         employees=employees, 
                         criteria=criteria,
                         min_rating=MIN_RATING,
                         max_rating=MAX_RATING)


@app.route('/evaluations/<eval_id>')
@login_required
def evaluations_view(eval_id):
    """View evaluation details."""
    evaluation = evaluations_store.find_by_id(eval_id)
    if not evaluation:
        flash('Evaluation not found.', 'danger')
        return redirect(url_for('evaluations_list'))
    
    # Check permissions
    role = session.get('role')
    if role == ROLE_EMPLOYEE and evaluation['employee_id'] != session['user_id']:
        flash('You do not have permission to view this evaluation.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Enrich data
    users_map = {u['id']: u for u in user_store.load()}
    criteria_map = eval_engine.get_criteria_map()
    
    evaluation['employee'] = users_map.get(evaluation['employee_id'], {})
    evaluation['evaluator'] = users_map.get(evaluation['evaluator_id'], {})
    evaluation['weighted_score'] = eval_engine.compute_weighted_score(
        evaluation['scores'], 
        criteria_map
    )
    
    # Add criterion details to scores
    score_details = []
    for crit_id, score in evaluation['scores'].items():
        if crit_id in criteria_map:
            score_details.append({
                'name': criteria_map[crit_id]['name'],
                'weight': criteria_map[crit_id]['weight'],
                'score': score,
                'weighted': score * criteria_map[crit_id]['weight']
            })
    
    return render_template('evaluations_view.html', 
                         evaluation=evaluation,
                         score_details=score_details)


# ============================================================================
# ROUTES - Reports & Exports
# ============================================================================

@app.route('/reports')
@role_required(ROLE_ADMIN, ROLE_EVALUATOR)
def reports():
    """Reports page."""
    summaries = eval_engine.get_all_employee_summaries(user_store)
    return render_template('reports.html', summaries=summaries)


@app.route('/export/detail')
@role_required(ROLE_ADMIN)
def export_detail():
    """Export detailed evaluations report."""
    try:
        evaluations = evaluations_store.load()
        criteria = criteria_store.load()
        users = user_store.load()
        
        filepath = exporter.export_evaluations_detail(evaluations, criteria, users)
        flash('Detail report exported successfully!', 'success')
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error exporting detail report: {e}")
        flash('An error occurred while exporting the report.', 'danger')
        return redirect(url_for('reports'))


@app.route('/export/summary')
@role_required(ROLE_ADMIN, ROLE_EVALUATOR)
def export_summary():
    """Export employee summary report."""
    try:
        summaries = eval_engine.get_all_employee_summaries(user_store)
        filepath = exporter.export_employee_summary(summaries)
        flash('Summary report exported successfully!', 'success')
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error exporting summary report: {e}")
        flash('An error occurred while exporting the report.', 'danger')
        return redirect(url_for('reports'))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message='Internal server error'), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Performance Evaluation System (Web)")
    app.run(debug=True, host='0.0.0.0', port=5000)