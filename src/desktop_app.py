import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
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

# Initialize stores
user_store = FileStore(config.USERS_FILE)
criteria_store = FileStore(config.CRITERIA_FILE)
evaluations_store = FileStore(config.EVALUATIONS_FILE)

# Initialize managers
auth_manager = AuthManager(user_store)
eval_engine = EvaluationEngine(criteria_store, evaluations_store)
exporter = ExcelExporter(config.EXPORTS_DIR)


class PerformanceEvalApp:
    """Main application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Performance Evaluation System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.current_user = None
        self.current_frame = None
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Show login
        self.show_login()
    
    def clear_frame(self):
        """Clear current frame."""
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_login(self):
        """Show login window."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill='both', expand=True)
        
        # Center frame
        login_frame = ttk.Frame(self.current_frame, padding=40)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(login_frame, text="Performance Evaluation System", 
                 font=('Arial', 20, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        username_entry = ttk.Entry(login_frame, width=30)
        username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        password_entry = ttk.Entry(login_frame, width=30, show='*')
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            
            user = auth_manager.authenticate(username, password)
            if user:
                self.current_user = user
                logger.info(f"User {username} logged in")
                self.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        
        ttk.Button(login_frame, text="Login", command=login).grid(row=3, column=0, columnspan=2, pady=20)
        
        username_entry.focus()
        password_entry.bind('<Return>', lambda e: login())
    
    def show_dashboard(self):
        """Show main dashboard."""
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill='both', expand=True)
        
        # Top bar
        top_bar = ttk.Frame(self.current_frame, padding=10)
        top_bar.pack(fill='x')
        
        ttk.Label(top_bar, text=f"Welcome, {self.current_user['full_name']}", 
                 font=('Arial', 14)).pack(side='left')
        ttk.Label(top_bar, text=f"Role: {self.current_user['role']}", 
                 font=('Arial', 10)).pack(side='left', padx=20)
        ttk.Button(top_bar, text="Logout", command=self.logout).pack(side='right')
        
        # Main content
        content = ttk.Frame(self.current_frame)
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left sidebar
        sidebar = ttk.Frame(content, width=200)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        
        ttk.Button(sidebar, text="Dashboard", width=20, 
                  command=self.show_dashboard).pack(pady=5)
        ttk.Button(sidebar, text="Evaluations", width=20, 
                  command=self.show_evaluations).pack(pady=5)
        
        if self.current_user['role'] in ['admin', 'evaluator']:
            ttk.Button(sidebar, text="Reports", width=20, 
                      command=self.show_reports).pack(pady=5)
        
        ttk.Button(sidebar, text="Criteria", width=20, 
                  command=self.show_criteria).pack(pady=5)
        
        if self.current_user['role'] == 'admin':
            ttk.Button(sidebar, text="Users", width=20, 
                      command=self.show_users).pack(pady=5)
        
        # Right content area
        self.content_area = ttk.Frame(content)
        self.content_area.pack(side='right', fill='both', expand=True)
        
        self.update_dashboard_content()
    
    def update_dashboard_content(self):
        """Update dashboard content area."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Dashboard", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        role = self.current_user['role']
        
        if role == 'admin':
            stats = ttk.Frame(self.content_area)
            stats.pack(pady=20)
            
            users = len(user_store.load())
            evals = len(evaluations_store.load())
            criteria = len(criteria_store.load())
            
            ttk.Label(stats, text=f"Total Users: {users}", 
                     font=('Arial', 14)).grid(row=0, column=0, padx=20)
            ttk.Label(stats, text=f"Evaluations: {evals}", 
                     font=('Arial', 14)).grid(row=0, column=1, padx=20)
            ttk.Label(stats, text=f"Criteria: {criteria}", 
                     font=('Arial', 14)).grid(row=0, column=2, padx=20)
        
        elif role == 'employee':
            summary = eval_engine.get_employee_summary(self.current_user['id'])
            
            stats = ttk.Frame(self.content_area)
            stats.pack(pady=20)
            
            ttk.Label(stats, text=f"My Evaluations: {summary['total_evaluations']}", 
                     font=('Arial', 14)).grid(row=0, column=0, padx=20)
            ttk.Label(stats, text=f"Average Score: {summary['average_score']:.2f}", 
                     font=('Arial', 14)).grid(row=0, column=1, padx=20)
    
    def show_evaluations(self):
        """Show evaluations list."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Evaluations", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        if self.current_user['role'] in ['admin', 'evaluator']:
            ttk.Button(self.content_area, text="New Evaluation", 
                      command=self.create_evaluation).pack(pady=5)
        
        # Create treeview
        tree_frame = ttk.Frame(self.content_area)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        tree = ttk.Treeview(tree_frame, columns=('ID', 'Date', 'Employee', 'Score', 'Status'),
                           show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        tree.heading('ID', text='ID')
        tree.heading('Date', text='Date')
        tree.heading('Employee', text='Employee')
        tree.heading('Score', text='Score')
        tree.heading('Status', text='Status')
        
        tree.column('ID', width=100)
        tree.column('Date', width=100)
        tree.column('Employee', width=200)
        tree.column('Score', width=80)
        tree.column('Status', width=80)
        
        tree.pack(fill='both', expand=True)
        
        # Load data
        role = self.current_user['role']
        if role == 'admin':
            evaluations = evaluations_store.load()
        elif role == 'evaluator':
            evaluations = evaluations_store.find_by(evaluator_id=self.current_user['id'])
        else:
            evaluations = evaluations_store.find_by(employee_id=self.current_user['id'])
        
        users_map = {u['id']: u.get('full_name', u['username']) for u in user_store.load()}
        criteria_map = eval_engine.get_criteria_map()
        
        for ev in evaluations:
            score = eval_engine.compute_weighted_score(ev['scores'], criteria_map)
            tree.insert('', 'end', values=(
                ev['id'],
                ev['date'],
                users_map.get(ev['employee_id'], 'Unknown'),
                f"{score:.2f}",
                ev['status']
            ))
    
    def create_evaluation(self):
        """Show create evaluation form."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Create Evaluation", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        form = ttk.Frame(self.content_area)
        form.pack(fill='both', expand=True, padx=20)
        
        # Employee selection
        ttk.Label(form, text="Employee:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        employees = user_store.find_by(role='employee')
        employee_var = tk.StringVar()
        employee_combo = ttk.Combobox(form, textvariable=employee_var, width=30)
        employee_combo['values'] = [f"{e['full_name']} ({e['id']})" for e in employees]
        employee_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Criteria scores
        criteria = criteria_store.load()
        score_vars = {}
        
        ttk.Label(form, text="Performance Scores:", 
                 font=('Arial', 12, 'bold')).grid(row=1, column=0, columnspan=2, pady=10)
        
        row = 2
        for criterion in criteria:
            ttk.Label(form, text=f"{criterion['name']} (Weight: {criterion['weight']}):").grid(
                row=row, column=0, sticky='e', padx=5, pady=5)
            
            score_var = tk.IntVar(value=3)
            score_vars[criterion['id']] = score_var
            
            score_frame = ttk.Frame(form)
            score_frame.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            
            for i in range(config.MIN_RATING, config.MAX_RATING + 1):
                ttk.Radiobutton(score_frame, text=str(i), variable=score_var, 
                              value=i).pack(side='left', padx=2)
            row += 1
        
        # Comments
        ttk.Label(form, text="Comments:").grid(row=row, column=0, sticky='ne', padx=5, pady=5)
        comments_text = scrolledtext.ScrolledText(form, width=40, height=5)
        comments_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Status
        ttk.Label(form, text="Status:").grid(row=row, column=0, sticky='e', padx=5, pady=5)
        status_var = tk.StringVar(value='draft')
        status_combo = ttk.Combobox(form, textvariable=status_var, width=15)
        status_combo['values'] = ['draft', 'final']
        status_combo.grid(row=row, column=1, sticky='w', padx=5, pady=5)
        row += 1
        
        def submit():
            try:
                # Get employee ID
                emp_text = employee_var.get()
                if not emp_text:
                    messagebox.showerror("Error", "Please select an employee")
                    return
                
                emp_id = emp_text.split('(')[1].strip(')')
                
                # Collect scores
                scores = {cid: var.get() for cid, var in score_vars.items()}
                
                # Create evaluation
                evaluation = Evaluation.create(
                    employee_id=emp_id,
                    evaluator_id=self.current_user['id'],
                    scores=scores,
                    comments=comments_text.get('1.0', 'end').strip(),
                    status=status_var.get()
                )
                
                if evaluations_store.create(evaluation):
                    messagebox.showinfo("Success", "Evaluation created successfully!")
                    self.show_evaluations()
                else:
                    messagebox.showerror("Error", "Failed to create evaluation")
            
            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                logger.error(f"Error creating evaluation: {e}")
                messagebox.showerror("Error", "An error occurred")
        
        button_frame = ttk.Frame(form)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create Evaluation", command=submit).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.show_evaluations).pack(side='left', padx=5)
    
    def show_users(self):
        """Show users management."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Users Management", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        ttk.Button(self.content_area, text="New User", 
                  command=self.create_user).pack(pady=5)
        
        # Create treeview
        tree_frame = ttk.Frame(self.content_area)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        tree = ttk.Treeview(tree_frame, columns=('Username', 'Name', 'Email', 'Role', 'Status'),
                           show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in ('Username', 'Name', 'Email', 'Role', 'Status'):
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill='both', expand=True)
        
        # Load users
        users = user_store.load()
        for user in users:
            tree.insert('', 'end', values=(
                user['username'],
                user.get('full_name', ''),
                user.get('email', ''),
                user['role'],
                'Active' if user.get('active', True) else 'Inactive'
            ))
    
    def create_user(self):
        """Show create user form."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New User")
        dialog.geometry("400x400")
        
        ttk.Label(dialog, text="Create New User", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form = ttk.Frame(dialog)
        form.pack(padx=20, pady=10)
        
        fields = {}
        
        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        fields['username'] = ttk.Entry(form, width=30)
        fields['username'].grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Password:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        fields['password'] = ttk.Entry(form, width=30, show='*')
        fields['password'].grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Full Name:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        fields['full_name'] = ttk.Entry(form, width=30)
        fields['full_name'].grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Email:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        fields['email'] = ttk.Entry(form, width=30)
        fields['email'].grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Role:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        role_var = tk.StringVar(value='employee')
        role_combo = ttk.Combobox(form, textvariable=role_var, width=28)
        role_combo['values'] = config.VALID_ROLES
        role_combo.grid(row=4, column=1, padx=5, pady=5)
        
        def submit():
            try:
                user_id = auth_manager.create_user(
                    username=fields['username'].get().strip(),
                    password=fields['password'].get(),
                    role=role_var.get(),
                    full_name=fields['full_name'].get().strip(),
                    email=fields['email'].get().strip()
                )
                
                if user_id:
                    messagebox.showinfo("Success", "User created successfully!")
                    dialog.destroy()
                    self.show_users()
                else:
                    messagebox.showerror("Error", "Username already exists")
            
            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
        
        ttk.Button(form, text="Create User", command=submit).grid(row=5, column=0, columnspan=2, pady=20)
    
    def show_criteria(self):
        """Show criteria list."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Evaluation Criteria", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        if self.current_user['role'] == 'admin':
            ttk.Button(self.content_area, text="New Criterion", 
                      command=self.create_criterion).pack(pady=5)
        
        # Create treeview
        tree_frame = ttk.Frame(self.content_area)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        tree = ttk.Treeview(tree_frame, columns=('Name', 'Weight', 'Description'),
                           show='headings')
        
        for col in ('Name', 'Weight', 'Description'):
            tree.heading(col, text=col)
        
        tree.column('Name', width=200)
        tree.column('Weight', width=100)
        tree.column('Description', width=400)
        
        tree.pack(fill='both', expand=True)
        
        # Load criteria
        criteria = criteria_store.load()
        for criterion in criteria:
            tree.insert('', 'end', values=(
                criterion['name'],
                criterion['weight'],
                criterion.get('description', '')
            ))
    
    def create_criterion(self):
        """Show create criterion form."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Criterion")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Create New Criterion", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form = ttk.Frame(dialog)
        form.pack(padx=20, pady=10)
        
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        name_entry = ttk.Entry(form, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Weight:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        weight_entry = ttk.Entry(form, width=30)
        weight_entry.insert(0, "1.0")
        weight_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Description:").grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        desc_text = scrolledtext.ScrolledText(form, width=30, height=5)
        desc_text.grid(row=2, column=1, padx=5, pady=5)
        
        def submit():
            try:
                criterion = Criterion.create(
                    name=name_entry.get().strip(),
                    weight=float(weight_entry.get()),
                    description=desc_text.get('1.0', 'end').strip()
                )
                
                if criteria_store.create(criterion):
                    messagebox.showinfo("Success", "Criterion created successfully!")
                    dialog.destroy()
                    self.show_criteria()
                else:
                    messagebox.showerror("Error", "Failed to create criterion")
            
            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
            except ValueError:
                messagebox.showerror("Error", "Invalid weight value")
        
        ttk.Button(form, text="Create Criterion", command=submit).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_reports(self):
        """Show reports page."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        ttk.Label(self.content_area, text="Reports & Exports", 
                 font=('Arial', 18, 'bold')).pack(pady=10)
        
        button_frame = ttk.Frame(self.content_area)
        button_frame.pack(pady=20)
        
        def export_detail():
            try:
                evaluations = evaluations_store.load()
                criteria = criteria_store.load()
                users = user_store.load()
                
                filepath = exporter.export_evaluations_detail(evaluations, criteria, users)
                messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
            except Exception as e:
                logger.error(f"Export error: {e}")
                messagebox.showerror("Error", "Failed to export report")
        
        def export_summary():
            try:
                summaries = eval_engine.get_all_employee_summaries(user_store)
                filepath = exporter.export_employee_summary(summaries)
                messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
            except Exception as e:
                logger.error(f"Export error: {e}")
                messagebox.showerror("Error", "Failed to export report")
        
        ttk.Button(button_frame, text="Export Detailed Report", 
                  command=export_detail).pack(pady=10)
        ttk.Button(button_frame, text="Export Summary Report", 
                  command=export_summary).pack(pady=10)
    
    def logout(self):
        """Logout and return to login."""
        self.current_user = None
        self.show_login()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()