from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import authenticate_user, deauthenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role in ['admin', 'sales']:
            return redirect(url_for('admin.admin'))
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            if user.role in ['admin', 'sales']:
                return redirect(url_for('admin.admin'))
            return redirect(url_for('public.index'))
        else:
            flash('Invalid username or password')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    deauthenticate_user(current_user.id, current_user.username)
    return redirect(url_for('auth.login'))
