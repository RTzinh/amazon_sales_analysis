# 🔧 Troubleshooting - Gemini API

## Problem: 404 error with the Gemini model

If you still see the error:
```
Error generating insights: 404 models/gemini-1.5-flash is not found
```

even after updating the code, it happens because **Streamlit is using a stale cache**.

---

## ✅ Quick Fix

### Option 1: Clear the cache from the menu (Recommended)
1. In the Streamlit app, click the **☰ menu** (three bars) in the top-right corner
2. Select **"Clear cache"**
3. Reload the page (F5)

### Option 2: Restart the server
1. Stop the Streamlit server (Ctrl+C in the terminal)
2. Restart it with:
```powershell
py -m streamlit run app.py
```

### Option 3: Force a full reload
In the terminal, run:
```powershell
# Windows PowerShell
Remove-Item -Recurse -Force $env:USERPROFILE\.streamlit\cache
py -m streamlit run app.py
```

---

## 🔍 Verification

The correct model configured in `ai_models.py`:
- ✅ Line 20: `model="gemini-2.5-flash"`
- ✅ Line 48: `genai.GenerativeModel('gemini-2.5-flash')`

No reference to `gemini-1.5-flash` exists in the current code.

---

## 📝 Available Gemini Models

Use one of these models with your API Key:
- **gemini-2.5-flash** (Recommended - latest)
- gemini-2.0-flash-exp
- gemini-1.5-pro
- gemini-1.5-flash-latest

---

## 🎯 After Clearing the Cache

1. Go to **🤖 AI Insights**
2. Enter your API Key
3. Test with **"🔄 Generate Insights"**
4. It should work perfectly! ✅

---

*Last updated: 12/01/2025*
