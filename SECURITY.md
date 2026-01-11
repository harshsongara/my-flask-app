# Security Guidelines

## 🔒 Data Privacy

### Database Storage
- **Location**: `instance/timetable.db` (local SQLite file)
- **Status**: ✅ Excluded from Git via `.gitignore`
- **Contains**: User accounts, passwords (hashed with bcrypt), tasks, and activity data

### What's Safe to Share
✅ **These files are safe in public repo:**
- Source code (`.py` files)
- Templates (`.html` files)
- Static files (`.css`, `.js`)
- Configuration structure (but not secrets)
- Requirements and documentation

### What's Protected
❌ **These are excluded from Git:**
- `instance/` folder (contains database)
- `.env` file (contains secrets)
- `*.db`, `*.sqlite` files
- `__pycache__/` and compiled Python files

## 🚀 Before Going Public

### 1. Generate a Secure Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and set it in your `.env` file:
```
SECRET_KEY=your-generated-secure-key-here
```

### 2. Verify .gitignore
Check that sensitive files are ignored:
```bash
git status
```
Should NOT show:
- `instance/timetable.db`
- `.env`

### 3. Clean Git History
If you accidentally committed sensitive data:
```bash
# Remove from Git but keep local file
git rm --cached instance/timetable.db
git rm --cached .env
git commit -m "Remove sensitive files"
```

### 4. Environment Variables
For production deployment, set these as environment variables:
- `SECRET_KEY` - Your secure secret key
- `DATABASE_URL` - Production database URL (PostgreSQL recommended)
- `FLASK_ENV=production`

## 🛡️ Password Security

### Current Protection
- ✅ Passwords are hashed using **Werkzeug security** (PBKDF2)
- ✅ Never stored in plain text
- ✅ One-way encryption (can't be reversed)

### How it Works
```python
# Registration - password is hashed
user.set_password(password)  # Stores hash, not password

# Login - compares hash
user.check_password(password)  # Returns True/False
```

## 📋 Security Checklist

Before making repository public:
- [ ] Database file is in `.gitignore`
- [ ] `.env` file is in `.gitignore`
- [ ] No sensitive data committed to Git history
- [ ] SECRET_KEY changed from default
- [ ] Production environment uses strong SECRET_KEY
- [ ] Production uses PostgreSQL (not SQLite)
- [ ] HTTPS enabled in production
- [ ] Debug mode disabled in production

## 🌐 Production Deployment

### Recommended Stack
- **Database**: PostgreSQL (not SQLite)
- **Server**: Gunicorn + Nginx
- **Platform**: Heroku, AWS, DigitalOcean, Railway
- **HTTPS**: Let's Encrypt / Platform SSL

### Why Not SQLite in Production?
- ✅ Great for development and personal use
- ❌ Not suitable for multiple concurrent users
- ❌ File-based (harder to backup/scale)
- ✅ PostgreSQL handles concurrent access better

## 📞 If Data is Exposed

If you accidentally commit sensitive data:

1. **Rotate all secrets immediately**
   - Change SECRET_KEY
   - Reset all user passwords
   
2. **Clean Git history**
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch instance/timetable.db" \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **Force push (if repo is yours)**
   ```bash
   git push origin --force --all
   ```

## ✅ Summary

**Your current setup is secure for local development!**
- Database is private (not in Git)
- Passwords are hashed
- Secrets are in `.env` (not in Git)

**Safe to make public** as long as you:
1. Never commit `.env` or `instance/` folder
2. Change default SECRET_KEY for production
3. Use PostgreSQL for production deployment
