# Deployment Guide - Royal Bank of India Application

This guide provides step-by-step instructions for deploying the Royal Bank application to various platforms.

## 🚀 Quick Deployment Options

### Option 1: Render.com (Recommended)

Render.com provides easy deployment with PostgreSQL database support.

#### Step 1: Prepare Repository
1. Push your code to GitHub/GitLab
2. Ensure all files are committed including:
   - `server/requirements.txt`
   - `render.yaml`
   - `Procfile`

#### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab
3. Connect your repository

#### Step 3: Create PostgreSQL Database
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Choose a name: `royal-bank-db`
4. Select region and plan
5. Note down the database credentials

#### Step 4: Deploy Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure settings:
   - **Name**: `royal-bank-app`
   - **Environment**: `Python 3`
   - **Build Command**: `cd server && pip install -r requirements.txt`
   - **Start Command**: `cd server && gunicorn -w 4 -b 0.0.0.0:$PORT src.main:app`

#### Step 5: Set Environment Variables
In the Environment section, add:
```
PYTHON_VERSION=3.11.0
DB_NAME=royal_bank_of_india
DB_USER=postgres
DB_PASSWORD=<your-db-password>
DB_HOST=<your-db-host>
DB_PORT=5432
SECRET_KEY=<generate-random-secret>
FLASK_ENV=production
```

#### Step 6: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Access your app at the provided URL

### Option 2: Heroku

#### Prerequisites
- Heroku CLI installed
- Git repository

#### Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create royal-bank-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set PYTHON_VERSION=3.11.0
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Open app
heroku open
```

### Option 3: DigitalOcean App Platform

#### Step 1: Create App
1. Go to DigitalOcean App Platform
2. Create new app from GitHub repository

#### Step 2: Configure Build
```yaml
name: royal-bank-app
services:
- name: web
  source_dir: /
  github:
    repo: your-username/royal-bank-app
    branch: main
  run_command: cd server && gunicorn -w 4 -b 0.0.0.0:$PORT src.main:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: PYTHON_VERSION
    value: "3.11.0"
  - key: SECRET_KEY
    value: "your-secret-key"
```

### Option 4: Railway

#### Steps
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically

## 🗄️ Database Setup

### PostgreSQL Database Creation

For any deployment platform, you'll need to create the database table:

```sql
-- Connect to your PostgreSQL database and run:
CREATE DATABASE royal_bank_of_india;

-- The application will automatically create tables on first run
-- Or you can create manually:
CREATE TABLE bank_transactions (
    id SERIAL PRIMARY KEY,
    aadhar_no BIGINT NOT NULL,
    name_of_user VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone_no BIGINT,
    nominee_aadhar_no BIGINT,
    balance BIGINT DEFAULT 0,
    withdrawal BIGINT DEFAULT 0,
    deposit BIGINT DEFAULT 0,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Providers

#### Render PostgreSQL
- Automatic backups
- SSL connections
- Easy integration

#### Heroku Postgres
- Hobby tier available
- Automatic provisioning
- CLI management

#### ElephantSQL
- Free tier available
- Managed PostgreSQL
- Global availability

#### Supabase
- PostgreSQL with additional features
- Real-time capabilities
- Free tier

## 🔧 Environment Variables Reference

### Required Variables
```env
# Database Configuration
DB_NAME=royal_bank_of_india
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=your_database_host
DB_PORT=5432

# Application Configuration
SECRET_KEY=your_very_secure_secret_key
FLASK_ENV=production
PYTHON_VERSION=3.11.0
```

### Optional Variables
```env
# For development
FLASK_DEBUG=False

# For custom configurations
PORT=5000
```

## 🔍 Deployment Verification

### Health Check Endpoints
```bash
# Check if app is running
curl https://your-app-url.com/health

# Expected response:
{
  "status": "healthy",
  "message": "Royal Bank API is running"
}
```

### Test Login
```bash
# Test login endpoint
curl -X POST https://your-app-url.com/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sk",
    "password": "00",
    "table_name": "bank_transactions"
  }'
```

## 🐛 Common Deployment Issues

### Issue 1: Build Failures
**Problem**: Dependencies not installing
**Solution**: 
- Check `requirements.txt` is in `server/` directory
- Verify Python version compatibility
- Check for missing system dependencies

### Issue 2: Database Connection
**Problem**: Cannot connect to database
**Solution**:
- Verify database credentials
- Check if database server is running
- Ensure database exists
- Check firewall/security group settings

### Issue 3: Static Files Not Loading
**Problem**: Frontend not displaying
**Solution**:
- Ensure files are in `server/src/static/`
- Check Flask static file configuration
- Verify build process copies files correctly

### Issue 4: CORS Errors
**Problem**: Frontend cannot call API
**Solution**:
- Verify CORS is enabled in Flask app
- Check if credentials are included in requests
- Ensure proper headers are set

## 📊 Performance Optimization

### Production Settings
```python
# In main.py for production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Gunicorn Configuration
```bash
# Recommended production command
gunicorn -w 4 -b 0.0.0.0:$PORT --timeout 120 src.main:app
```

### Database Optimization
- Use connection pooling
- Add database indexes
- Regular maintenance

## 🔒 Security Checklist

- [ ] Environment variables set securely
- [ ] Database credentials protected
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] Secret key is random and secure
- [ ] Debug mode disabled in production
- [ ] CORS properly configured
- [ ] Input validation enabled
- [ ] SQL injection protection active

## 📈 Monitoring & Maintenance

### Logging
- Check application logs regularly
- Monitor error rates
- Set up alerts for critical issues

### Backups
- Regular database backups
- Code repository backups
- Environment configuration backups

### Updates
- Keep dependencies updated
- Monitor security advisories
- Test updates in staging environment

## 🆘 Support & Troubleshooting

### Getting Help
1. Check application logs
2. Review this deployment guide
3. Test locally first
4. Check platform-specific documentation

### Useful Commands
```bash
# Check logs (Heroku)
heroku logs --tail

# Restart app (Heroku)
heroku restart

# Database console (Heroku)
heroku pg:psql

# Check environment variables
heroku config
```

---

**Need Help?** Create an issue in the repository with:
- Platform you're deploying to
- Error messages
- Steps you've tried
- Environment details

