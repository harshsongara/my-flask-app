# TimeTable - Quick Start Guide

## ✅ Installation Complete!

Your TimeTable application is now fully set up and running!

## 🚀 Access the Application

The application is running at: **http://localhost:5000**

## 📝 Getting Started

### 1. Create an Account
1. Click "Register here" on the login page
2. Enter a username, email, and password
3. Click "Register"

### 2. Log In
- Username: (your username)
- Password: (your password)

### 3. Create Your First Task
1. Click "+ New Task" button
2. Fill in the details:
   - **Title**: What you need to do
   - **Description**: Optional details
   - **Completion Window**: Choose daily, weekly, monthly, or custom
   - **Priority**: Low, Medium, or High
   - **Tags**: Optional (comma-separated)
3. Click "Create Task"

### 4. Explore Features

**Dashboard**: Overview of your progress
- Today's completion rate
- Weekly stats
- Monthly trends
- Upcoming tasks and recent completions

**Tasks Page**: Manage all your tasks
- Filter by status (Active, At Risk, Overdue, Completed)
- Mark tasks complete with checkmark button
- Edit or archive tasks

**Daily View**: Focus on today's tasks
- See what's due today
- Track today's completion rate

**Weekly View**: 7-day overview
- See this week's tasks
- Visual trend chart
- Weekly completion stats

**Monthly View**: Long-term perspective
- Month-long task view
- 30-day activity chart
- Monthly completion trends

## 🎯 Task Management Philosophy

TimeTable uses **flexible completion windows** instead of rigid time slots:

- **Daily Tasks**: Complete by end of day
- **Weekly Tasks**: 7 days from creation
- **Monthly Tasks**: 30 days from creation
- **Custom Tasks**: Set your own deadline (e.g., 3 days, 2 weeks)

Tasks automatically update their status:
- ✅ **Completed**: Task finished
- 📋 **Active**: Normal status
- ⚠️ **At Risk**: Less than 20% time remaining
- ❌ **Overdue**: Deadline passed

## ⌨️ Keyboard Shortcuts

- `Ctrl+N` (or `Cmd+N` on Mac): Create new task

## 🛠️ Commands

### Stop the Server
Press `CTRL+C` in the terminal running the application

### Restart the Server
```bash
python run.py
```

### Create a Demo User (Optional)
```bash
flask create-demo-user
```
- Username: `demo`
- Password: `demo123`

### Reset Database (⚠️ Deletes all data)
```bash
flask reset-db
```

### Open Flask Shell (Advanced)
```bash
flask shell
```

## 📂 Project Structure

```
d:\TimeTable\
├── app/                    # Application code
│   ├── auth.py            # Login/register
│   ├── tasks.py           # Task management
│   ├── dashboard.py       # Analytics
│   ├── models.py          # Database models
│   └── utils.py           # Helper functions
├── templates/             # HTML templates
├── static/                # CSS and JavaScript
├── instance/              # Database location
│   └── timetable.db      # Your data
└── run.py                # Application entry point
```

## 💡 Tips

1. **Start Small**: Create a few daily tasks to get familiar
2. **Use Tags**: Organize tasks with tags like "work", "personal", "urgent"
3. **Check Daily View**: Make it a habit to review daily view each morning
4. **Review Weekly**: Use weekly view to see your productivity trends
5. **Adjust Windows**: If tasks often go overdue, try longer windows

## 🐛 Troubleshooting

### Application won't start
- Make sure no other application is using port 5000
- Check that the database exists: `d:\TimeTable\instance\timetable.db`
- Reinitialize database: `python init_db.py`

### Can't log in
- Double-check username and password
- Create a new account if you forgot credentials
- Use demo account: username `demo`, password `demo123` (if created)

### Tasks not appearing
- Make sure you're logged in to the correct account
- Check different status filters (Active, Completed, etc.)
- Verify tasks weren't archived

## 📚 Next Steps

1. **Read the System Design**: See `SYSTEM_DESIGN.md` for architecture details
2. **Customize**: Edit CSS in `static/css/` to change colors/styling
3. **Extend**: Add features by modifying the Python files in `app/`
4. **Deploy**: Follow deployment guide in `README.md` for production

## 🎉 You're All Set!

Enjoy your flexible, stress-free task management!

---

**Need help?** Refer to `README.md` or `SYSTEM_DESIGN.md`
