# 🚀 Free Deployment Guide for Real Estate MVP

## Option 1: Railway (Recommended - Easiest)

### Step 1: Prepare Your Code
1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### Step 2: Deploy on Railway
1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your repository**
5. **Railway will automatically detect Django and deploy!**

### Step 3: Configure Environment Variables
In Railway dashboard, go to your project → Variables tab:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://... (Railway provides this automatically)
```

### Step 4: Run Migrations (Easiest Method)
**Option A: Use Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and connect to your project
railway login
railway link

# Run migrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py setup_gifts
```

**Option B: Add to your code (Alternative)**
Create a `railway_startup.py` file in your project root:
```python
import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

# Run migrations automatically
execute_from_command_line(['manage.py', 'migrate'])
execute_from_command_line(['manage.py', 'setup_gifts'])
```

Then update your `Procfile`:
```
web: python railway_startup.py && gunicorn realestate_project.wsgi:application
```

---

## Option 2: Render (Also Great - Easier Console Access)

### Step 1: Prepare Your Code
Same as Railway - push to GitHub

### Step 2: Deploy on Render
1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New" → "Web Service"**
4. **Connect your GitHub repo**
5. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn realestate_project.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3.11 (specify this version)
   - **Region:** Choose closest to your users

**Note:** Render uses the regular `Procfile` (not the Railway one with startup script)

**Important:** Make sure to set Python version to 3.11 in Render settings to avoid compatibility issues!

### Step 3: Add Database
1. **In Render dashboard → "New" → "PostgreSQL"**
2. **Choose "Free" plan**
3. **Copy the database URL**
4. **Go back to your Web Service**
5. **Go to "Environment" tab**
6. **Add these environment variables:**
   ```
   DATABASE_URL=postgresql://... (from step 3)
   SECRET_KEY=your-secret-key-here-make-it-long-and-random
   DEBUG=False
   ```

### Step 4: Run Migrations (Easy!)
1. **Go to your Web Service dashboard**
2. **Click "Shell" button** (this actually works!)
3. **Run these commands:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py setup_gifts
   ```

### Step 5: Deploy
1. **Click "Manual Deploy" → "Deploy latest commit"**
2. **Wait for deployment to complete**
3. **Your app will be live at:** `https://your-app-name.onrender.com`

---

## Option 3: PythonAnywhere (Free Tier)

### Step 1: Create Account
1. **Go to [pythonanywhere.com](https://pythonanywhere.com)**
2. **Sign up for free account**

### Step 2: Upload Code
1. **Go to Files tab**
2. **Upload your project as ZIP file**
3. **Extract in your home directory**

### Step 3: Configure Web App
1. **Go to Web tab → "Add a new web app"**
2. **Choose "Manual configuration"**
3. **Select Python 3.10**
4. **In WSGI file, replace content with:**
   ```python
   import os
   import sys
   
   path = '/home/YOUR_USERNAME/RealestateMVP'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'realestate_project.settings'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

### Step 4: Install Dependencies
In Console tab:
```bash
pip3.10 install --user -r requirements.txt
python3.10 manage.py migrate
python3.10 manage.py createsuperuser
python3.10 manage.py setup_gifts
```

---

## Option 4: Heroku (Limited Free)

### Step 1: Install Heroku CLI
Download from [devcenter.heroku.com](https://devcenter.heroku.com)

### Step 2: Deploy
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py setup_gifts
```

---

## 🎯 Recommended: Railway

**Why Railway?**
- ✅ Completely free for small projects
- ✅ Automatic deployments from GitHub
- ✅ Built-in PostgreSQL database
- ✅ Easy environment variable management
- ✅ No credit card required
- ✅ Great for Django apps

**Your app will be live at:** `https://your-project-name.railway.app`

---

## 🔧 Post-Deployment Steps

1. **Create Admin User:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Set up Gifts:**
   ```bash
   python manage.py setup_gifts
   ```

3. **Test All Features:**
   - Admin login
   - Agent login
   - Customer login
   - Add projects, agents, customers
   - Add payments
   - Check gift system

---

## 🚨 Important Notes

- **Never commit `db.sqlite3` to Git** (it's in .gitignore)
- **Use environment variables for secrets**
- **Set DEBUG=False in production**
- **Backup your database regularly**
- **Monitor your app's performance**

---

## 🆘 Need Help?

If you run into issues:
1. Check the deployment logs
2. Verify all environment variables are set
3. Make sure migrations ran successfully
4. Test locally first with `DEBUG=False`

**Good luck with your deployment! 🚀**
