import re
import hashlib
import time
from datetime import datetime, timedelta
from flask import jsonify, request
from models import RateLimit, User
from app import db
import uuid

def validate_phone_number(phone_number):
    """Validate Indonesian phone number format"""
    phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')
    
    # Indonesian phone number patterns
    patterns = [
        r'^62\d{8,12}$',  # +62 format
        r'^0\d{8,12}$',   # 0 format
        r'^\d{9,13}$'     # Raw number
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    
    return False

def normalize_phone_number(phone_number):
    """Normalize phone number to standard format"""
    phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')
    
    if phone.startswith('0'):
        phone = '62' + phone[1:]
    elif not phone.startswith('62'):
        phone = '62' + phone
    
    return phone

def rate_limit_check(identifier, action, limit=10, window_minutes=1, identifier_type='user'):
    """Check if action is within rate limits"""
    try:
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Clean old entries
        RateLimit.query.filter(
            RateLimit.identifier == str(identifier),
            RateLimit.action == action,
            RateLimit.window_start < window_start
        ).delete()
        
        # Count current requests in window
        current_count = RateLimit.query.filter(
            RateLimit.identifier == str(identifier),
            RateLimit.action == action,
            RateLimit.window_start >= window_start
        ).count()
        
        if current_count >= limit:
            return False
        
        # Add new rate limit entry
        rate_limit = RateLimit(
            identifier=str(identifier),
            identifier_type=identifier_type,
            action=action,
            window_start=datetime.utcnow()
        )
        
        db.session.add(rate_limit)
        db.session.commit()
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Rate limit check error: {str(e)}")
        return True  # Allow on error to prevent breaking functionality

def generate_api_response(success, message, data=None, status_code=200):
    """Generate standardized API response"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': str(uuid.uuid4())[:8]
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def hash_string(text):
    """Generate SHA-256 hash of string"""
    return hashlib.sha256(text.encode()).hexdigest()

def generate_session_token():
    """Generate secure session token"""
    return str(uuid.uuid4()).replace('-', '')

def get_client_ip():
    """Get client IP address"""
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))

def get_user_agent():
    """Get user agent string"""
    return request.headers.get('User-Agent', '')

def sanitize_input(text, max_length=None):
    """Sanitize user input"""
    if not text:
        return ''
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', str(text))
    
    # Limit length if specified
    if max_length:
        text = text[:max_length]
    
    return text.strip()

def format_currency(amount):
    """Format currency for Indonesian Rupiah"""
    return f"Rp {amount:,.0f}"

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return 'N/A'
    
    return dt.strftime('%d/%m/%Y %H:%M')

def calculate_subscription_expiry(subscription_type):
    """Calculate subscription expiry date"""
    if subscription_type == 'premium_monthly':
        return datetime.utcnow() + timedelta(days=30)
    elif subscription_type == 'premium_yearly':
        return datetime.utcnow() + timedelta(days=365)
    else:
        return None

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_username_suggestion(base_name):
    """Generate username suggestions"""
    suggestions = []
    base_clean = re.sub(r'[^a-zA-Z0-9]', '', base_name.lower())
    
    for i in range(5):
        suggestion = f"{base_clean}{i+1}"
        if not User.query.filter_by(username=suggestion).first():
            suggestions.append(suggestion)
    
    return suggestions

def check_password_strength(password):
    """Check password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"

def detect_proxy_or_vpn(ip_address):
    """Basic proxy/VPN detection"""
    # This is a simplified check - in production you'd use a proper service
    suspicious_ranges = [
        '10.',     # Private IP
        '172.',    # Private IP
        '192.168.' # Private IP
    ]
    
    for range_start in suspicious_ranges:
        if ip_address.startswith(range_start):
            return True
    
    return False

def log_security_event(event_type, description, severity='warning'):
    """Log security events"""
    from auth import log_action
    from auth import get_current_user
    
    user = get_current_user()
    user_id = user.id if user else None
    
    log_action(user_id, f'security_{event_type}', description, severity)

def mask_sensitive_data(text, mask_char='*', visible_chars=4):
    """Mask sensitive data like phone numbers, emails"""
    if not text or len(text) <= visible_chars:
        return text
    
    return text[:visible_chars] + mask_char * (len(text) - visible_chars)

def get_time_ago(dt):
    """Get human readable time ago string"""
    if not dt:
        return 'Never'
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def validate_transaction_id(transaction_id):
    """Validate transaction ID format"""
    # Basic validation - adjust based on payment provider requirements
    if not transaction_id or len(transaction_id) < 10:
        return False
    
    # Check for valid characters (alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]+$', transaction_id):
        return False
    
    return True

def calculate_success_rate(successful, total):
    """Calculate success rate percentage"""
    if total == 0:
        return 0.0
    return (successful / total) * 100

def generate_backup_codes(count=10):
    """Generate backup codes for 2FA"""
    codes = []
    for _ in range(count):
        code = ''.join([str(uuid.uuid4().hex)[:8].upper()])
        codes.append(code)
    return codes
