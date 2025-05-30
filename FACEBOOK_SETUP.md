
# Facebook Login Setup Guide - Complete

## Kredensial Admin Terbaru
- **Username**: deltapro_admin
- **Password**: !tsMWiWeVuU$aC0xlJda
- **API Key**: ADMIN_FYW0A80GLMNJEEEX7I4TGHE6ZHLOZ6EPXGAGQAOL

## Domain Configuration untuk Replit

### Current Domain URLs yang Dibutuhkan:
Pastikan domain berikut didaftarkan di Facebook App:

```
Domain: [YOUR-REPL].replit.app
OAuth Callback: https://[YOUR-REPL].replit.app/auth/facebook_callback
Privacy Policy: https://[YOUR-REPL].replit.app/privacy
Terms of Service: https://[YOUR-REPL].replit.app/disclaimer
Data Deletion: https://[YOUR-REPL].replit.app/data-deletion
```

## Langkah Setup Facebook App

### 1. Create Facebook App
1. Kunjungi https://developers.facebook.com
2. Click **"Create App"**
3. Pilih **"Consumer"** → **"Continue"**
4. Masukkan:
   - App Name: `DeltaPro OTP Service`
   - Contact Email: [your email]

### 2. Configure Basic Settings
1. Go to **Settings** → **Basic**
2. Set **App Domains**: `[YOUR-REPL].replit.app`
3. Add **Privacy Policy URL**: `https://[YOUR-REPL].replit.app/privacy`
4. Add **Terms of Service URL**: `https://[YOUR-REPL].replit.app/disclaimer`
5. Add **Data Deletion Request URL**: `https://[YOUR-REPL].replit.app/data-deletion`

### 3. Setup Facebook Login
1. Click **"Add Product"** → **"Facebook Login"**
2. Go to **Facebook Login** → **Settings**
3. Add **Valid OAuth Redirect URIs**:
   ```
   https://[YOUR-REPL].replit.app/auth/facebook_callback
   ```
4. Enable **Use Strict Mode for Redirect URIs**

### 4. Copy Credentials
1. Go to **Settings** → **Basic**
2. Copy **App ID** and **App Secret**
3. Paste ke Admin Panel Facebook Configuration

## Mengatasi Error Domain

### Error: "Domain tidak termasuk dalam domain aplikasi"
**Solusi:**
1. Pastikan domain exact match di Facebook App Settings
2. Check App Domains di Basic Settings
3. Verify OAuth Redirect URI exact match
4. Untuk Replit, selalu gunakan `.replit.app` domain

### Error: "Failed to get Facebook access token"
**Solusi:**
1. Verify App ID dan App Secret benar
2. Check redirect URI exact match
3. Pastikan app status "Live" atau user sebagai tester

## Testing Mode Setup

### Untuk Development Testing:
1. Go to **App Review** → **Requests**
2. Add test users di **Roles** → **Test Users**
3. Test login dengan test accounts

### Untuk Production:
1. Complete App Review process
2. Submit permissions untuk review
3. Provide detailed use case description

## Advanced Configuration

### Webhook Setup (Optional):
```
Webhook URL: https://[YOUR-REPL].replit.app/webhook/facebook
Verify Token: [generate random token]
```

### Permissions Required:
- `public_profile` (automatically included)
- `email` (requires app review for production)

## Troubleshooting Commands

### Check Current Domain:
```bash
echo $REPLIT_DEV_DOMAIN
```

### Verify SSL Certificate:
```bash
curl -I https://[YOUR-REPL].replit.app/
```

### Test Facebook Callback:
```bash
curl -I https://[YOUR-REPL].replit.app/auth/facebook_callback
```

## Admin Panel Features

### Facebook Configuration Panel:
- **URL**: `/admin/facebook-config`
- **Features**:
  - Set App ID dan App Secret
  - Enable/Disable Facebook Login
  - Test connection
  - Auto-sync settings
  - Copy required URLs

### User Login Status:
- **URL**: `/admin/user-login-status`
- **Features**:
  - View all login methods
  - Monitor Facebook vs Password logins
  - User statistics
  - Login history

## Security Notes

1. **App Secret**: Simpan dengan aman, jangan expose di client-side
2. **HTTPS Only**: Facebook requires HTTPS untuk production
3. **Domain Verification**: Exact match required untuk security
4. **Rate Limiting**: Monitor API usage untuk avoid limits

## Status Monitoring

### Check Facebook Integration Status:
```python
# Via Admin Panel atau direct query
from models import FacebookConfig
config = FacebookConfig.get_config()
print(f"Enabled: {config.is_enabled}")
print(f"App ID: {config.app_id}")
```

### Monitor Login Methods:
```python
from models import User
facebook_users = User.query.filter_by(login_method='facebook').count()
password_users = User.query.filter_by(login_method='password').count()
```

## Troubleshooting

### Common Issues:

1. **"Domain tidak termasuk dalam domain aplikasi"**
   - Pastikan domain di Facebook App Settings match dengan URL aplikasi
   - Untuk Replit: gunakan HTTPS URL (.replit.dev)
   - Tambahkan domain di Facebook App > Settings > Basic > App Domains

2. **"Failed to get Facebook access token"**
   - Periksa App ID dan App Secret di admin panel
   - Pastikan App tidak dalam mode Development dengan user terbatas
   - Periksa apakah OAuth Redirect URIs sudah benar

3. **Database Schema Error**
   - Jalankan: `python update_user_schema.py`
   - Restart aplikasi

4. **Login dengan Username/Password Error**
   - Pastikan kolom login_method sudah ada di database
   - Jalankan create_admin.py untuk membuat admin user

### Admin Credentials:
- Username: deltapro_admin
- Password: !tsMWiWeVuU$aC0xlJda
- API Key: ADMIN_FYW0A80GLMNJEEEX7I4TGHE6ZHLOZ6EPXGAGQAOL').count()
```
