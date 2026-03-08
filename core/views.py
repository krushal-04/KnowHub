from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import os

from .models import Category, Document, Comment, Notification
from .forms import RegisterForm, LoginForm, DocumentUploadForm, DocumentEditForm, CommentForm, ProfileUpdateForm


def notify(recipient, ntype, message, document=None):
    Notification.objects.create(
        recipient=recipient,
        notification_type=ntype,
        message=message,
        document=document,
    )


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    query    = request.GET.get('q', '')
    cat_id   = request.GET.get('category', '')
    docs     = Document.objects.filter(is_active=True).select_related('uploader', 'category')

    if query:
        docs = docs.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(uploader__username__icontains=query)
        )
    if cat_id:
        docs = docs.filter(category__id=cat_id)

    categories = Category.objects.all()
    return render(request, 'core/home.html', {
        'recent_docs':      docs[:8],
        'categories':       categories,
        'query':            query,
        'cat_id':           cat_id,
        'total_docs':       Document.objects.filter(is_active=True).count(),
        'total_users':      User.objects.count(),
        'total_categories': categories.count(),
    })


# ── Auth ──────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to KnowledgeShare, {user.username}!')
        return redirect('home')
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── Document List ─────────────────────────────────────────────────────────────
def document_list(request):
    query  = request.GET.get('q', '')
    cat_id = request.GET.get('category', '')
    sort   = request.GET.get('sort', '-uploaded_at')

    docs = Document.objects.filter(is_active=True).select_related('uploader', 'category')

    if query:
        docs = docs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(uploader__username__icontains=query))
    if cat_id:
        docs = docs.filter(category__id=cat_id)
    if sort in ['-uploaded_at', 'uploaded_at', 'title', '-download_count']:
        docs = docs.order_by(sort)

    paginator = Paginator(docs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/document_list.html', {
        'page_obj':    page_obj,
        'categories':  Category.objects.all(),
        'query':       query,
        'cat_id':      cat_id,
        'sort':        sort,
        'total_count': docs.count(),
    })


# ── Document Detail ───────────────────────────────────────────────────────────
def document_detail(request, pk):
    document     = get_object_or_404(Document, pk=pk, is_active=True)
    comments     = document.comments.select_related('author').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to post a comment.')
            return redirect('login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.document = document
            c.author   = request.user
            c.save()
            if document.uploader != request.user:
                notify(
                    document.uploader, 'comment',
                    f'{request.user.username} commented on your document "{document.title}"',
                    document=document,
                )
            messages.success(request, 'Comment posted!')
            return redirect('document_detail', pk=pk)

    related = Document.objects.filter(category=document.category, is_active=True).exclude(pk=pk)[:4]
    return render(request, 'core/document_detail.html', {
        'document':     document,
        'comments':     comments,
        'comment_form': comment_form,
        'related_docs': related,
    })


# ── Upload ────────────────────────────────────────────────────────────────────
@login_required
def document_upload(request):
    form = DocumentUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.uploader = request.user
        doc.save()
        messages.success(request, f'"{doc.title}" uploaded successfully!')
        return redirect('document_detail', pk=doc.pk)
    return render(request, 'core/document_upload.html', {'form': form})


# ── Edit ──────────────────────────────────────────────────────────────────────
@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_active=True)
    if doc.uploader != request.user:
        messages.error(request, 'You can only edit your own documents.')
        return redirect('document_detail', pk=pk)
    form = DocumentEditForm(request.POST or None, request.FILES or None, instance=doc)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Document updated!')
        return redirect('document_detail', pk=pk)
    return render(request, 'core/document_edit.html', {'form': form, 'document': doc})


# ── Delete ────────────────────────────────────────────────────────────────────
@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_active=True)
    if doc.uploader != request.user:
        messages.error(request, 'You can only delete your own documents.')
        return redirect('document_detail', pk=pk)
    if request.method == 'POST':
        title = doc.title
        doc.delete()
        messages.success(request, f'"{title}" deleted.')
        return redirect('my_documents')
    return render(request, 'core/document_confirm_delete.html', {'document': doc})


# ── Download ──────────────────────────────────────────────────────────────────
@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_active=True)
    try:
        path = doc.file.path
        if not os.path.exists(path):
            raise Http404
        doc.download_count += 1
        doc.save(update_fields=['download_count'])
        response = FileResponse(open(path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
        return response
    except Exception:
        raise Http404


# ── My Documents ──────────────────────────────────────────────────────────────
@login_required
def my_documents(request):
    docs = Document.objects.filter(uploader=request.user, is_active=True)
    return render(request, 'core/my_documents.html', {
        'documents':       docs,
        'total_downloads': sum(d.download_count for d in docs),
        'total_comments':  sum(d.comment_count() for d in docs),
    })


# ── Notifications ─────────────────────────────────────────────────────────────
@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    page_obj = Paginator(notifs, 20).get_page(request.GET.get('page'))
    return render(request, 'core/notifications.html', {'page_obj': page_obj})


@login_required
@require_POST
def clear_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('notifications')


# ── Profile ───────────────────────────────────────────────────────────────────
@login_required
def profile(request):
    docs = Document.objects.filter(uploader=request.user, is_active=True)
    form = ProfileUpdateForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return render(request, 'core/profile.html', {
        'documents':       docs[:6],
        'total_downloads': sum(d.download_count for d in docs),
        'total_comments':  Comment.objects.filter(author=request.user).count(),
        'form':            form,
    })


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    docs = Document.objects.filter(uploader=profile_user, is_active=True)
    return render(request, 'core/public_profile.html', {
        'profile_user':    profile_user,
        'documents':       docs,
        'total_downloads': sum(d.download_count for d in docs),
    })


# ── Category ──────────────────────────────────────────────────────────────────
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    docs     = Document.objects.filter(category=category, is_active=True)
    page_obj = Paginator(docs, 12).get_page(request.GET.get('page'))
    return render(request, 'core/category_detail.html', {
        'category':   category,
        'page_obj':   page_obj,
        'categories': Category.objects.all(),
    })


# ── Comment Delete ────────────────────────────────────────────────────────────
@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    doc_pk  = comment.document.pk
    if comment.author == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, 'Comment deleted.')
    else:
        messages.error(request, 'You cannot delete this comment.')
    return redirect('document_detail', pk=doc_pk)
