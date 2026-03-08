# 📚 KnowledgeShare — Knowledge Sharing Portal

A full Django web app for uploading, sharing, and discovering documents.

---

## ⚡ Quick Setup (Windows)

**Option A — Automatic (recommended):**
1. Extract the zip
2. Open the `knowledge_portal` folder
3. Double-click `setup.bat`
4. After it finishes, run:
   ```
   venv\Scripts\activate
   python manage.py runserver
   ```
5. Open http://127.0.0.1:8000

---

**Option B — Manual:**
```cmd
cd knowledge_portal
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python setup_demo.py
python manage.py runserver
```

---

## 🔑 Login Accounts (after setup_demo.py)

| Role  | Username | Password    |
|-------|----------|-------------|
| Admin | admin    | admin123    |
| User  | alice    | password123 |
| User  | bob      | password123 |
| User  | carol    | password123 |

Admin panel: http://127.0.0.1:8000/admin

---

## 📁 Project Structure

```
knowledge_portal/
├── manage.py              ← Run Django commands here
├── requirements.txt       ← Python packages
├── setup.bat              ← Windows one-click setup
├── setup_demo.py          ← Seeds categories and demo users
├── .env                   ← Environment variables (SECRET_KEY etc.)
├── .gitignore
├── knowledge_portal/
│   ├── settings.py        ← Django configuration
│   ├── urls.py            ← Main URL routing
│   └── wsgi.py
└── core/                  ← Main application
    ├── models.py          ← Category, Document, Comment, Notification
    ├── views.py           ← All page logic
    ├── forms.py           ← All forms
    ├── urls.py            ← App URLs
    ├── admin.py           ← Admin panel config
    ├── context_processors.py
    ├── migrations/
    └── templates/core/    ← All HTML pages
        ├── base.html
        ├── home.html
        ├── register.html
        ├── login.html
        ├── document_list.html
        ├── document_detail.html
        ├── document_upload.html
        ├── document_edit.html
        ├── document_confirm_delete.html
        ├── my_documents.html
        ├── notifications.html
        ├── profile.html
        ├── public_profile.html
        └── category_detail.html
```

---

## ✅ Features

- Register, Login, Logout
- Upload documents (PDF, Word, Excel, PPT, TXT)
- Browse & search all documents
- Download documents (with counter)
- Comment on documents
- Notifications when someone comments on your doc
- Notifications when admin removes your doc
- Edit / Delete your own documents only
- Public profiles for each user
- Category browsing
- Admin panel to manage everything
