from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user
from ...models import User, ActivityLog, db
from datetime import datetime
from flask import session

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        
        # Log activity
        activity = ActivityLog(
            user_id=user.id,
            username=user.username,
            activity_type='login',
            activity_date=datetime.utcnow(),
            details=f'User {username} logged in'
        )
        db.session.add(activity)
        db.session.commit()
        return user
    return None

def deauthenticate_user(user_id, username):
    activity = ActivityLog(
        user_id=user_id,
        username=username,
        activity_type='logout',
        activity_date=datetime.utcnow(),
        details=f'User {username} logged out'
    )
    db.session.add(activity)
    db.session.commit()
    
    logout_user()
    session.clear()
    return True
