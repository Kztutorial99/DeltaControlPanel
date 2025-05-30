import os
import requests
from flask import Blueprint, request, redirect, url_for, session, flash
from app import db
from models import User, FacebookConfig
from auth import log_action
from datetime import datetime
import uuid

facebook_bp = Blueprint('facebook_auth', __name__)

@facebook_bp.route('/facebook_login')
def facebook_login():
    """Initiate Facebook OAuth login"""
    # Get Facebook config from database
    config = FacebookConfig.get_config()
    
    if not config.is_enabled or not config.app_id:
        flash('Facebook login is currently disabled', 'error')
        return redirect(url_for('login'))
    
    # Get the redirect URI - ensure it matches Facebook app settings
    redirect_uri = request.url_root.rstrip('/') + url_for('facebook_auth.facebook_callback')
    # Ensure https for production and Replit
    if 'replit' in request.host or 'repl.co' in request.host or request.is_secure:
        redirect_uri = redirect_uri.replace('http://', 'https://')
    
    # Store redirect_uri in session for callback verification
    session['facebook_redirect_uri'] = redirect_uri
    
    # Log for debugging
    print(f"Facebook login redirect URI: {redirect_uri}")
    
    # Facebook OAuth URL
    facebook_oauth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={config.app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=email,public_profile&"
        f"response_type=code"
    )
    
    return redirect(facebook_oauth_url)

@facebook_bp.route('/facebook_callback')
def facebook_callback():
    """Handle Facebook OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    # Handle user denial or error
    if error:
        if error == 'access_denied':
            flash('Facebook login was cancelled by user', 'info')
        else:
            flash(f'Facebook login error: {error_description or error}', 'error')
        return redirect(url_for('login'))
    
    if not code:
        flash('No authorization code received from Facebook', 'error')
        return redirect(url_for('login'))
    
    # Get Facebook config from database
    config = FacebookConfig.get_config()
    
    if not config.is_enabled or not config.app_id or not config.app_secret:
        flash('Facebook login is not properly configured', 'error')
        return redirect(url_for('login'))
    
    try:
        # Construct proper redirect URI - must match exactly with Facebook app settings
        redirect_uri = request.url_root.rstrip('/') + url_for('facebook_auth.facebook_callback')
        # Ensure https for production and Replit
        if 'replit' in request.host or 'repl.co' in request.host:
            redirect_uri = redirect_uri.replace('http://', 'https://')
        
        # Log redirect URI for debugging
        print(f"Facebook callback redirect URI: {redirect_uri}")
        
        # Exchange code for access token
        token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        token_params = {
            'client_id': config.app_id,
            'client_secret': config.app_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }
        
        token_response = requests.get(token_url, params=token_params, timeout=10)
        
        # Log the response for debugging
        print(f"Facebook token response status: {token_response.status_code}")
        print(f"Facebook token response: {token_response.text}")
        
        if token_response.status_code != 200:
            flash(f'Facebook API error: {token_response.status_code} - {token_response.text}', 'error')
            return redirect(url_for('login'))
        
        token_data = token_response.json()
        
        if 'error' in token_data:
            error_msg = token_data.get('error', {})
            if isinstance(error_msg, dict):
                error_text = error_msg.get('message', 'Unknown error')
            else:
                error_text = str(error_msg)
            flash(f'Facebook token error: {error_text}', 'error')
            return redirect(url_for('login'))
        
        if 'access_token' not in token_data:
            flash('Failed to get Facebook access token - no token in response', 'error')
            return redirect(url_for('login'))
        
        access_token = token_data['access_token']
        
        # Get user information from Facebook
        user_url = 'https://graph.facebook.com/v18.0/me'
        user_params = {
            'fields': 'id,name,email,picture',
            'access_token': access_token
        }
        
        user_response = requests.get(user_url, params=user_params, timeout=10)
        
        print(f"Facebook user response status: {user_response.status_code}")
        print(f"Facebook user response: {user_response.text}")
        
        if user_response.status_code != 200:
            flash(f'Failed to get user info from Facebook: {user_response.status_code}', 'error')
            return redirect(url_for('login'))
        
        user_data = user_response.json()
        
        if 'error' in user_data:
            error_msg = user_data.get('error', {}).get('message', 'Unknown error')
            flash(f'Facebook user info error: {error_msg}', 'error')
            return redirect(url_for('login'))
        
        # Extract user information
        facebook_id = user_data.get('id')
        name = user_data.get('name', '')
        email = user_data.get('email', f'facebook_{facebook_id}@deltapro.local')
        picture_url = user_data.get('picture', {}).get('data', {}).get('url', '')
        
        # Check if user exists by email or Facebook ID
        user = User.query.filter((User.email == email) | (User.facebook_id == facebook_id)).first()
        
        if not user:
            # Create new user
            username = f"fb_{facebook_id}"
            # Make sure username is unique
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"fb_{facebook_id}_{counter}"
                counter += 1
            
            user = User()
            user.username = username
            user.email = email
            user.facebook_id = facebook_id
            user.login_method = 'facebook'
            user.is_active = True
            user.balance = 0.0
            user.set_password(str(uuid.uuid4()))  # Random password since they login via Facebook
            user.generate_api_key()
            
            db.session.add(user)
            db.session.commit()
            
            log_action(user.id, 'facebook_register', f'New user registered via Facebook: {email}')
            flash(f'Welcome to DeltaPro, {name}! Your account has been created.', 'success')
        else:
            # Update existing user's Facebook info
            user.facebook_id = facebook_id
            user.login_method = 'facebook'
            log_action(user.id, 'facebook_login', f'User logged in via Facebook: {email}')
            flash(f'Welcome back, {user.username}!', 'success')
        
        # Log the user in
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        session['login_method'] = 'facebook'
        
        # Update login info
        user.last_login = datetime.utcnow()
        user.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        db.session.commit()
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash('An error occurred during Facebook login. Please try again.', 'error')
        log_action(None, 'facebook_login_error', f'Facebook login error: {str(e)}', 'error')
        return redirect(url_for('login'))