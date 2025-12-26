# Step-by-Step Guide to Run the Project

## Prerequisites
- Python 3.8 or higher installed
- MongoDB Atlas account (or local MongoDB)
- Internet connection (for MongoDB Atlas)

---

## STEP 1: Set MongoDB URI Environment Variable

### Windows:
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```bash
   cd "C:\Users\DELL\Downloads\Data Base\final_project"
   ```
3. Run the setup script:
   ```bash
   setup_mongodb_uri.bat
   ```
4. **IMPORTANT:** Close and reopen your terminal/command prompt for the environment variable to take effect.

### OR Manually (Windows):
```bash
setx MONGODB_URI "mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority"
```
Then close and reopen your terminal.

### Linux/Mac:
```bash
chmod +x setup_mongodb_uri.sh
./setup_mongodb_uri.sh
```

---

## STEP 2: Install Python Dependencies

1. Open a new terminal/command prompt (after setting the environment variable)
2. Navigate to the project folder:
   ```bash
   cd "C:\Users\DELL\Downloads\Data Base\final_project"
   ```
3. Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install:
   - FastAPI
   - Uvicorn
   - PyMongo
   - Pandas
   - Scikit-learn
   - Matplotlib
   - Seaborn
   - And other dependencies

---

## STEP 3: Verify MongoDB Connection

1. Test if the MongoDB URI is set correctly:
   ```bash
   python -c "import os; print(os.getenv('MONGODB_URI'))"
   ```
   You should see the MongoDB connection string.

2. Test MongoDB connection:
   ```bash
   python -c "from backend.database import client; client.admin.command('ping'); print('✅ MongoDB Connected!')"
   ```

---

## STEP 4: Initialize the Project

This step will:
- Check MongoDB connection
- Create database indexes
- Load dataset from Excel file
- Train the ML model

1. Run the initialization script:
   ```bash
   python init_project.py
   ```

2. Wait for completion. You should see:
   ```
   ✅ MongoDB is running and accessible
   ✅ Created index on users.email
   ✅ Created index on predictions.user_id
   ... (more indexes)
   ✅ Dataset loaded successfully: X records
   ✅ Model trained and saved: 1 model(s)
   ✅ Initialization Complete!
   ```

3. If you see any errors:
   - **MongoDB connection error**: Make sure you set the MONGODB_URI environment variable and restarted your terminal
   - **Dataset not found**: Make sure `data/Book4.xlsx` exists in the project folder
   - **Dependencies error**: Run `pip install -r requirements.txt` again

---

## STEP 5: Start the FastAPI Backend Server

### Option A: Using Batch File (Windows - Easiest)
```bash
start_backend.bat
```

### Option B: Manual Start
1. Navigate to backend folder:
   ```bash
   cd backend
   ```
2. Start the server:
   ```bash
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. You should see output like:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   ✅ MongoDB connection verified on startup
   📊 Creating MongoDB indexes...
   ✅ Created index on users.email
   ... (more indexes)
   ✅ Indexes created successfully
   INFO:     Application startup complete.
   ```

4. **Keep this terminal window open!** The server must keep running.

---

## STEP 6: Verify Backend is Running

1. Open your web browser
2. Visit: `http://127.0.0.1:8000`
   - You should see JSON with API information
3. Visit: `http://127.0.0.1:8000/docs`
   - You should see Swagger UI with all API endpoints
4. Visit: `http://127.0.0.1:8000/health`
   - You should see health status with MongoDB connection info

---

## STEP 7: Open the Frontend

### Option A: Direct File Opening
1. Navigate to the `frontend` folder
2. Open `login.html` in your web browser
   - Right-click → Open with → Your browser

### Option B: Using Live Server (Recommended)
1. If you have VS Code with Live Server extension:
   - Right-click on `frontend/login.html`
   - Select "Open with Live Server"
2. Or use Python's built-in server:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
   Then visit: `http://127.0.0.1:5500/login.html`

---

## STEP 8: Use the Application

1. **Create an Account:**
   - Click "Sign Up" or go to `signup.html`
   - Enter name, email, and password
   - Click "Sign Up"
   - You'll be redirected to login

2. **Login:**
   - Enter your email and password
   - Click "Login"
   - You'll be redirected to the dashboard

3. **View Dashboard:**
   - See analytics and charts
   - View statistics (total sales, averages, etc.)
   - See visualizations (bar charts, pie charts, histograms)

4. **Make Predictions:**
   - Go to the "Predict" or "AI Insights" page
   - Enter quantity and sales price
   - Click "Predict"
   - See the result (Good or Bad)

5. **View Profile:**
   - Click on your profile
   - See your account information
   - Delete account if needed (uses transaction)

---

## STEP 9: Test API Endpoints (Optional)

You can test endpoints using:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **Browser**: Visit endpoints directly
- **Postman/Insomnia**: For POST requests

### Example API Calls:

1. **Health Check:**
   ```
   GET http://127.0.0.1:8000/health
   ```

2. **View Indexes:**
   ```
   GET http://127.0.0.1:8000/indexes/info
   ```

3. **Test Aggregation:**
   ```
   GET http://127.0.0.1:8000/aggregations/total-sales
   ```

4. **Explain Query Performance:**
   ```
   GET http://127.0.0.1:8000/explain/query?collection=users&query_field=email&query_value=test@test.com
   ```

---

## Troubleshooting

### Problem: "MongoDB connection failed"
**Solution:**
- Make sure you set the MONGODB_URI environment variable
- Restart your terminal after setting it
- Check internet connection (for MongoDB Atlas)
- Verify the connection string is correct

### Problem: "Module not found" errors
**Solution:**
```bash
pip install -r requirements.txt
```

### Problem: "Dataset collection is empty"
**Solution:**
```bash
python init_project.py
```
Or use the "Load Dataset" button on the dashboard

### Problem: "No model found"
**Solution:**
```bash
python init_project.py
```
Or call: `POST http://127.0.0.1:8000/train-model`

### Problem: Backend won't start on port 8000
**Solution:**
- Check if another application is using port 8000
- Change the port in `start_backend.bat` or command:
  ```bash
  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
  ```

### Problem: Frontend can't connect to backend
**Solution:**
- Make sure backend is running (check terminal)
- Check browser console (F12) for errors
- Verify backend URL in `frontend/app.js` is `http://127.0.0.1:8000`

### Problem: Charts not showing
**Solution:**
- Make sure dataset is loaded
- Check browser console for errors
- Verify backend is running
- Refresh the page (Ctrl+F5)

---

## Quick Reference Commands

```bash
# Set MongoDB URI (Windows)
setup_mongodb_uri.bat

# Install dependencies
pip install -r requirements.txt

# Initialize project
python init_project.py

# Start backend (Windows)
start_backend.bat

# Start backend (Manual)
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Test MongoDB connection
python -c "from backend.database import client; client.admin.command('ping'); print('✅ Connected!')"
```

---

## Project Structure Reminder

```
final_project/
├── backend/          # FastAPI application
├── frontend/         # HTML/CSS/JS files
├── ml/              # ML training scripts
├── mongodb/         # MongoDB queries and scripts
├── data/            # Dataset Excel file
├── outputs/          # Generated charts
├── init_project.py  # Initialization script
├── requirements.txt  # Python dependencies
└── README.md        # Project documentation
```

---

## Success Indicators

✅ **Backend Running:**
- Terminal shows "Uvicorn running on http://127.0.0.1:8000"
- `http://127.0.0.1:8000/health` returns success

✅ **Frontend Working:**
- Can create account
- Can login
- Dashboard shows data and charts
- Can make predictions

✅ **Everything Connected:**
- No errors in browser console (F12)
- No errors in backend terminal
- Data appears on dashboard
- Charts render correctly

---

## Need Help?

1. Check `README.md` for detailed documentation
2. Check `VERIFICATION_CHECKLIST.md` for feature list
3. Check browser console (F12) for frontend errors
4. Check backend terminal for server errors
5. Verify all steps were completed in order

---

**🎉 Once all steps are complete, your application should be fully functional!**

