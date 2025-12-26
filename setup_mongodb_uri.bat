@echo off
echo ========================================
echo Setting MongoDB URI Environment Variable
echo ========================================
echo.

REM Set MongoDB URI for current session
setx MONGODB_URI "mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority"

echo.
echo ✅ MongoDB URI has been set!
echo.
echo IMPORTANT: You need to restart your terminal/command prompt
echo for the environment variable to take effect.
echo.
echo After restarting, you can verify with:
echo   echo %%MONGODB_URI%%
echo.
pause

