# Cleanup Instructions

## Files/Folders to Delete

The following files and folders are no longer needed and can be safely deleted:

### 1. Old Project Files
- `app.py/` - Old Streamlit app files (not used)
- `modules/` - Old module files in root (duplicates of backend/modules)
- `requirements.txt/` - Old requirements file (use backend/requirements.txt)
- `README.md.txt` - Duplicate README file

### 2. Unused Frontend
- `frontend/` - Next.js frontend (not used, we use mobile app instead)

### 3. Duplicate Data
- `data/` - Root level data folder (backend has its own data/ folder)

## How to Delete (Windows)

### Using File Explorer
1. Navigate to `C:\Users\91940\Documents\AI_Edu_Assessment`
2. Delete the folders/files listed above
3. Empty Recycle Bin

### Using Command Prompt
```cmd
cd C:\Users\91940\Documents\AI_Edu_Assessment
rmdir /s /q app.py
rmdir /s /q modules
rmdir /s /q requirements.txt
rmdir /s /q frontend
rmdir /s /q data
del README.md.txt
```

### Using PowerShell
```powershell
cd C:\Users\91940\Documents\AI_Edu_Assessment
Remove-Item -Recurse -Force app.py
Remove-Item -Recurse -Force modules
Remove-Item -Recurse -Force requirements.txt
Remove-Item -Recurse -Force frontend
Remove-Item -Recurse -Force data
Remove-Item -Force README.md.txt
```

## What to Keep

### Essential Files
- `backend/` - Backend API code
- `mobile/` - Mobile app code
- `documentation/` - All documentation
- `README.md` - Main readme
- `.gitignore` - Git ignore file

### Configuration Files
- `backend/requirements.txt` - Python dependencies
- `mobile/package.json` - Node dependencies
- `backend/.env` - Environment variables (not in git)

## After Cleanup

Your project structure should look like:

```
AI_Edu_Assessment/
├── backend/
│   ├── main.py
│   ├── modules/
│   ├── requirements.txt
│   └── data/
├── mobile/
│   ├── App.tsx
│   ├── package.json
│   └── ...
├── documentation/
│   ├── ARCHITECTURE.md
│   ├── RAG_PIPELINE.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   └── PROJECT_OVERVIEW.md
├── README.md
├── .gitignore
└── CLEANUP_INSTRUCTIONS.md (this file)
```

## Verification

After cleanup, verify:
1. Backend still runs: `cd backend && uvicorn main:app`
2. Mobile app still works: `cd mobile && npm start`
3. All documentation is accessible
4. No broken imports or references

