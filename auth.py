from functools import wraps
from flask import session, redirect, url_for, request, abort
from models import User, AuditLog
from app import db
from datetime import datetime

def get_current_user():
    """Get the currently logged in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        
        user = get_current_user()
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        
        user = get_current_user()
        if not user or not user.is_active or not user.is_admin:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def premium_required(f):
    """Decorator to require premium subscription for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        
        user = get_current_user()
        if not user or not user.is_active:
            session.clear()
            return redirect(url_for('login'))
        
        if not user.is_subscription_active():
            return redirect(url_for('premium'))
        
        return f(*args, **kwargs)
    return decorated_function

def log_action(user_id, action, description, severity='info'):
    """Log user actions for audit purposes"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
            user_agent=request.headers.get('User-Agent', ''),
            severity=severity,
            created_at=datetime.utcnow()
        )
        
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        # Don't let logging errors break the application
        db.session.rollback()
        print(f"Logging error: {str(e)}")

def check_session_security():
    """Check session security (device binding, IP validation, etc.)"""
    user = get_current_user()
    if not user:
        return False
    
    current_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    current_device = request.headers.get('User-Agent', '')
    
    # For premium users, enforce device binding
    if user.is_premium and user.device_id and user.device_id != current_device:
        log_action(user.id, 'device_violation', 'Device binding violation detected', 'warning')
        return False
    
    # Update last seen info
    user.ip_address = current_ip
    user.last_login = datetime.utcnow()
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return True

def validate_api_key(api_key):
    """Validate API key and return user"""
    if not api_key:
        return None
    
    user = User.query.filter_by(api_key=api_key, is_active=True).first()
    if user:
        # Update last seen
        user.last_login = datetime.utcnow()
        user.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    return user
