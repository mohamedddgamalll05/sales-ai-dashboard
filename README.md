# Full Stack MongoDB + FastAPI + ML Project

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB
Make sure MongoDB is running on `mongodb://127.0.0.1:27017`

### 3. Initialize Project (Load Data & Train Model)
**IMPORTANT:** Run this first to populate the dataset and train the model!
```bash
python init_project.py
```
This will:
- Check MongoDB connection
- Load `data/Book4.xlsx` into MongoDB if dataset is empty
- Train the ML model
- Save the model to MongoDB

**Alternative:** If you prefer to do it manually:
```bash
cd ml
python train_model.py
```

### 4. Start FastAPI Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend will run on `http://127.0.0.1:8000`

**Or use the batch file (Windows):**
```bash
start_backend.bat
```

### 5. Open Frontend
Open `frontend/dashboard.html` in your browser (or use Live Server)

**Note:** You must be logged in to view the dashboard. If you don't have an account, create one from the login page.

## Troubleshooting

### Dashboard shows error or all zeros?

1. **"Cannot connect to backend" error**
   - Make sure FastAPI is running: `cd backend && uvicorn main:app --reload`
   - Check it's on port 8000: http://127.0.0.1:8000/health
   - Check browser console (F12) for detailed error messages

2. **Dashboard shows all zeros**
   - Load dataset: Run `python init_project.py` or use the "Load Dataset Now" button on the dashboard
   - Refresh dashboard page (Ctrl+F5)

3. **Charts not showing**
   - Check backend terminal for Python errors
   - Make sure dataset collection has data
   - Check browser console (F12) for JavaScript errors
   - Charts will only appear if there is data in the dataset

4. **MongoDB connection errors**
   - Start MongoDB: `mongod` (or start MongoDB service)
   - Verify connection: `mongosh` should work

5. **Infinite reload loop**
   - Clear browser localStorage: Open browser console (F12) and run `localStorage.clear()`
   - Make sure you're logged in before accessing dashboard

### Quick Test
Visit http://127.0.0.1:8000/health to check if backend is running

## Project Structure
- `backend/` - FastAPI application
- `frontend/` - HTML/CSS/JS files
- `ml/` - ML training script
- `mongodb/` - MongoDB queries, aggregations, indexes, transactions
- `data/` - Dataset Excel file
- `outputs/` - Generated charts and screenshots
