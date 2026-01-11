# Deployment Guide for Render/Heroku

## Files for Deployment

### 1. wsgi.py
- **Purpose**: WSGI entry point for production servers
- **Used by**: Gunicorn, uWSGI, and other WSGI servers
- **Command**: `gunicorn wsgi:app`

### 2. run.py
- **Purpose**: Development server entry point
- **Used by**: Local development only
- **Command**: `python run.py`

## Render Deployment

### Quick Deploy Steps:

1. **Push to GitHub** (database and .env excluded automatically)

2. **Create New Web Service on Render:**
   - Connect your GitHub repo
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Environment**: Python 3

3. **Set Environment Variables** in Render dashboard:
   ```
   SECRET_KEY=<generate-secure-key>
   FLASK_ENV=production
   DATABASE_URL=<render-will-provide-postgres-url>
   ```

4. **Add PostgreSQL Database** (optional but recommended):
   - Create PostgreSQL database in Render
   - Copy DATABASE_URL to environment variables

### Generate Secure Key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secure-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Initialize database
heroku run flask init-db
```

## Environment Variables Needed

```env
SECRET_KEY=your-generated-secure-secret-key
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## Local vs Production

| Feature | Local (run.py) | Production (wsgi.py) |
|---------|----------------|---------------------|
| Debug | ON | OFF |
| Server | Flask dev server | Gunicorn |
| Database | SQLite | PostgreSQL |
| Command | `python run.py` | `gunicorn wsgi:app` |
| Port | 5000 | Dynamic (set by platform) |

## Important Notes

- ✅ `wsgi.py` created - ready for deployment
- ✅ `Procfile` created - tells Render/Heroku how to run
- ✅ `gunicorn` added to requirements.txt
- ✅ Database and secrets excluded from Git
- ⚠️  Change SECRET_KEY before deploying
- ⚠️  Use PostgreSQL in production (not SQLite)
