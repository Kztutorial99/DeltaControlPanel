from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    subscription_expiry = db.Column(db.DateTime)
    balance = db.Column(db.Float, default=0.0)
    device_id = db.Column(db.String(128))
    ip_address = db.Column(db.String(45))
    last_login = db.Column(db.DateTime)
    login_method = db.Column(db.String(20), default='password')  # password, facebook
    facebook_id = db.Column(db.String(50))  # Store Facebook user ID
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    otp_requests = db.relationship('OTPRequest', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)
    payments = db.relationship('Payment', foreign_keys='Payment.user_id', backref='user', lazy=True)
    verified_payments = db.relationship('Payment', foreign_keys='Payment.verified_by', backref='verifier', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_api_key(self):
        self.api_key = str(uuid.uuid4()).replace('-', '')
    
    def is_subscription_active(self):
        if not self.is_premium:
            return False
        if self.subscription_expiry:
            return datetime.utcnow() < self.subscription_expiry
        return False
    
    def get_otp_cooldown(self):
        """Get OTP cooldown time in seconds"""
        if self.is_premium:
            return 15  # 15 seconds for premium
        else:
            return 60  # 1 minute for free users
    
    def can_use_all_services(self):
        """Check if user can use all OTP services"""
        return self.is_premium
    
    def can_send_multiple_numbers(self):
        """Check if user can send to multiple numbers"""
        return self.is_premium
    
    def __repr__(self):
        return f'<User {self.username}>'

class OTPProvider(db.Model):
    __tablename__ = 'otp_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    cost_per_request = db.Column(db.Float, default=0.0)
    is_premium_only = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    rate_limit_per_minute = db.Column(db.Integer, default=10)
    success_rate = db.Column(db.Float, default=0.0)
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    otp_requests = db.relationship('OTPRequest', backref='provider', lazy=True)
    
    def update_success_rate(self):
        if self.total_requests > 0:
            self.success_rate = (self.successful_requests / self.total_requests) * 100
        else:
            self.success_rate = 0.0

class OTPRequest(db.Model):
    __tablename__ = 'otp_requests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('otp_providers.id'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    otp_code = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending')  # pending, success, failed, expired
    response_data = db.Column(db.Text)
    error_message = db.Column(db.Text)
    cost = db.Column(db.Float, default=0.0)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<OTPRequest {self.id}>'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_admin_message = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # OVO, DANA, etc.
    transaction_id = db.Column(db.String(100), unique=True)
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, verified, failed, expired
    subscription_type = db.Column(db.String(50))  # premium_monthly, premium_yearly
    verification_data = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Payment {self.id}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    request_data = db.Column(db.Text)
    response_data = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')  # info, warning, error, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'

class RateLimit(db.Model):
    __tablename__ = 'rate_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False)  # user_id, ip_address, etc.
    identifier_type = db.Column(db.String(50), nullable=False)  # user, ip, api_key
    action = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=1)
    window_start = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RateLimit {self.identifier}:{self.action}>'

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_value(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set_value(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

class FacebookConfig(db.Model):
    __tablename__ = 'facebook_config'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(50), nullable=False, default='')
    app_secret = db.Column(db.String(100), nullable=False, default='')
    is_enabled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_config(cls):
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config
    
    def update_config(self, app_id, app_secret, is_enabled=True):
        self.app_id = app_id
        self.app_secret = app_secret
        self.is_enabled = is_enabled
        self.updated_at = datetime.utcnow()
        db.session.commit()

class UserApiKey(db.Model):
    __tablename__ = 'user_api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def generate_key(self):
        self.api_key = str(uuid.uuid4()).replace('-', '')

class CustomOTPService(db.Model):
    __tablename__ = 'custom_otp_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    prefix_code = db.Column(db.String(10), nullable=False)
    service_code = db.Column(db.Text, nullable=False)  # Python code for the service
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_maintenance = db.Column(db.Boolean, default=False, nullable=False)
    is_premium_only = db.Column(db.Boolean, default=False, nullable=False)
    cost_per_request = db.Column(db.Float, default=0.0)
    success_rate = db.Column(db.Float, default=0.0)
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_success_rate(self):
        if self.total_requests > 0:
            self.success_rate = (self.successful_requests / self.total_requests) * 100
        else:
            self.success_rate = 0.0

class SystemReport(db.Model):
    __tablename__ = 'system_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    report_type = db.Column(db.String(50), nullable=False)  # 'bug', 'error', 'feedback'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    error_details = db.Column(db.Text)  # Stack trace, error logs, etc.
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    url = db.Column(db.String(255))
    browser_info = db.Column(db.Text)
    is_auto_generated = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_resolved(self, admin_id, notes=None):
        self.status = 'resolved'
        self.resolved_by = admin_id
        self.resolved_at = datetime.utcnow()
        if notes:
            self.admin_notes = notes

class MessageReply(db.Model):
    __tablename__ = 'message_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    original_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    reply_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_global = db.Column(db.Boolean, default=False, nullable=False)
    icon = db.Column(db.String(50), default='fa-bell')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    push_notifications = db.Column(db.Boolean, default=True, nullable=False)
    marketing_notifications = db.Column(db.Boolean, default=False, nullable=False)
    maintenance_notifications = db.Column(db.Boolean, default=True, nullable=False)
    payment_notifications = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyClaim(db.Model):
    __tablename__ = 'daily_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    claim_date = db.Column(db.Date, default=datetime.utcnow().date)
    amount = db.Column(db.Float, default=5000.0)
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'claim_date', name='unique_daily_claim'),)

class SaldoTransaction(db.Model):
    __tablename__ = 'saldo_transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # claim, admin_transfer, payment, usage
    amount = db.Column(db.Float, nullable=False)
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    reference_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('User', foreign_keys=[admin_id], backref='saldo_transfers_sent')
    user = db.relationship('User', foreign_keys=[user_id], backref='saldo_transactions')
