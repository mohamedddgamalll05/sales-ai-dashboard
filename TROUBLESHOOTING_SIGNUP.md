# Troubleshooting: Signup Not Creating Users in MongoDB

## ✅ Yes, it should be created automatically!

When you sign up, the user **should be created automatically** in MongoDB. If it's not working, follow these steps:

---

## Step 1: Verify Backend is Running

1. **Check if backend server is running:**
   - Look at your terminal where you ran `start_backend.bat`
   - You should see: `Uvicorn running on http://127.0.0.1:8000`

2. **Test backend connection:**
   - Open browser and go to: `http://127.0.0.1:8000/health`
   - You should see MongoDB connection status

3. **If backend is NOT running:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

---

## Step 2: Test MongoDB Connection

Run the test script to verify MongoDB connection:

```bash
cd backend
python test_db_connection.py
```

**Expected output:**
```
✅ Database module imported successfully
✅ MongoDB connection successful!
✅ Connected to database: sales_db
✅ Collections found: ['users', 'dataset', ...]
✅ Users collection exists with X document(s)
✅ All tests passed!
```

**If you see errors:**
- Check your `MONGODB_URI` environment variable
- Make sure you restarted terminal after setting it
- Check internet connection (for MongoDB Atlas)

---

## Step 3: Check Browser Console for Errors

1. **Open signup page** in browser
2. **Open Developer Tools** (Press F12)
3. **Go to Console tab**
4. **Try to sign up**
5. **Look for errors** in red

**Common errors:**
- `Failed to fetch` → Backend not running
- `CORS error` → Backend CORS not configured (should be fixed)
- `Network error` → Backend URL incorrect

---

## Step 4: Check Backend Terminal for Errors

When you try to sign up, **watch your backend terminal**. You should see:

```
📝 Signup request received: email=test@example.com, name=Test User
✅ MongoDB connection verified
📝 Inserting user document: test@example.com
✅ User inserted successfully with _id: 67890abcdef1234567890123
✅ Verified: User document exists in database
✅ User created successfully: test@example.com
```

**If you see errors:**
- `MongoDB connection error` → Connection issue
- `User already exists` → Email already registered
- `Failed to insert user` → Database write issue

---

## Step 5: Verify in MongoDB Compass

1. **Open MongoDB Compass**
2. **Connect to:** `mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db`
3. **Navigate to:** `sales_db` → `users` collection
4. **Check if your user exists:**
   - Click on `users` collection
   - Look for documents with your email

**If collection is empty:**
- Signup is not reaching the database
- Check backend logs for errors
- Verify backend is running

---

## Step 6: Test Signup Endpoint Directly

Test the signup API directly using browser or Postman:

1. **Open browser and go to:** `http://127.0.0.1:8000/docs`
2. **Find the `/signup` endpoint**
3. **Click "Try it out"**
4. **Enter test data:**
   ```json
   {
     "name": "Test User",
     "email": "test@example.com",
     "password": "test123"
   }
   ```
5. **Click "Execute"**
6. **Check response:**
   - Should return `{"success": true}`
   - Check backend terminal for logs
   - Check MongoDB Compass for new user

---

## Common Issues and Solutions

### Issue 1: "Failed to fetch" Error

**Problem:** Backend not running or not accessible

**Solution:**
```bash
# Make sure backend is running
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

### Issue 2: MongoDB Connection Error

**Problem:** Can't connect to MongoDB Atlas

**Solution:**
1. Check `MONGODB_URI` environment variable:
   ```bash
   python -c "import os; print(os.getenv('MONGODB_URI'))"
   ```

2. If empty, set it:
   ```bash
   setup_mongodb_uri.bat
   # Then restart terminal
   ```

3. Test connection:
   ```bash
   cd backend
   python test_db_connection.py
   ```

---

### Issue 3: "User already exists" Error

**Problem:** Email is already registered

**Solution:**
- Use a different email
- Or check MongoDB Compass to see existing users

---

### Issue 4: No Errors but User Not Created

**Problem:** Silent failure

**Solution:**
1. Check backend terminal logs (should show detailed logs now)
2. Run test script: `python backend/test_db_connection.py`
3. Check MongoDB Compass directly
4. Verify database name is `sales_db` (not `final_project`)

---

## Quick Diagnostic Checklist

- [ ] Backend server is running (`http://127.0.0.1:8000/health` works)
- [ ] MongoDB connection works (`test_db_connection.py` passes)
- [ ] Browser console shows no errors (F12)
- [ ] Backend terminal shows signup logs
- [ ] MongoDB Compass shows `sales_db` database
- [ ] `users` collection exists in `sales_db`

---

## Manual Test Steps

1. **Start backend:**
   ```bash
   start_backend.bat
   ```

2. **Test connection:**
   ```bash
   cd backend
   python test_db_connection.py
   ```

3. **Open signup page** in browser

4. **Open browser console** (F12)

5. **Fill signup form** and submit

6. **Check:**
   - Browser console for errors
   - Backend terminal for logs
   - MongoDB Compass for new user

---

## Still Not Working?

If after all these steps it's still not working:

1. **Share the error message** from:
   - Browser console (F12)
   - Backend terminal
   - `test_db_connection.py` output

2. **Verify:**
   - Backend is running
   - MongoDB connection works
   - No firewall blocking connections

3. **Check MongoDB Atlas:**
   - Network Access: Make sure your IP is allowed (or use 0.0.0.0/0 for all)
   - Database Access: User `sales_user` has read/write permissions

---

## Expected Behavior

When signup works correctly:

1. ✅ User fills form and clicks "Sign Up"
2. ✅ Frontend sends POST request to `http://127.0.0.1:8000/signup`
3. ✅ Backend receives request and logs it
4. ✅ Backend connects to MongoDB
5. ✅ Backend inserts user document into `sales_db.users`
6. ✅ Backend returns `{"success": true}`
7. ✅ Frontend shows success message
8. ✅ User appears in MongoDB Compass

**If any step fails, you'll see an error message!**


