#!/usr/bin/env python
"""
Run ONCE after migrate to seed demo data.
Usage: python setup_demo.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_portal.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Category

print("\n Seeding KnowledgeShare...\n")

CATEGORIES = [
    ("Study Notes",          "Academic notes, summaries, and study guides",     "📖"),
    ("Technology",           "Programming, software, and tech topics",           "💻"),
    ("Business",             "Business plans, case studies, and strategies",     "💼"),
    ("Science",              "Research papers and scientific content",            "🔬"),
    ("Mathematics",          "Formulas, proofs, and problem sets",               "📐"),
    ("Language & Writing",   "Essays, writing guides, and language learning",    "✍️"),
    ("Health & Medicine",    "Medical guides and health information",             "🏥"),
    ("Arts & Design",        "Creative guides and design resources",              "🎨"),
]

for name, desc, icon in CATEGORIES:
    _, created = Category.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
    status = "created" if created else "exists "
    print(f"  {icon}  [{status}] {name}")

print()


if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("   Admin created   → username: admin    password: admin123")
else:
    print("    Admin already exists")

# Demo users
for uname, email, pw, fname, lname in [
    ('alice', 'alice@demo.com', 'password123', 'Alice', 'Chen'),
    ('bob',   'bob@demo.com',   'password123', 'Bob',   'Smith'),
    ('carol', 'carol@demo.com', 'password123', 'Carol', 'Jones'),
]:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, pw, first_name=fname, last_name=lname)
        print(f"   User created    → username: {uname:<8} password: {pw}")
    else:
        print(f"    User {uname} already exists")

print("""
╔═══════════════════════════════════════════════╗
║            ✅  Setup Complete!                ║
╠═══════════════════════════════════════════════╣
║  Run:  python manage.py runserver             ║
║  Open: http://127.0.0.1:8000                  ║
║  Admin: http://127.0.0.1:8000/admin           ║
║         admin / admin123                      ║
║  Demo users (password: password123):          ║
║         alice  |  bob  |  carol               ║
╚═══════════════════════════════════════════════╝
""")
