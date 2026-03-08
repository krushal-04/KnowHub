from django.urls import path
from . import views

urlpatterns = [
    path('',                                views.home,                name='home'),
    path('register/',                       views.register_view,       name='register'),
    path('login/',                          views.login_view,          name='login'),
    path('logout/',                         views.logout_view,         name='logout'),
    path('documents/',                      views.document_list,       name='document_list'),
    path('documents/upload/',               views.document_upload,     name='document_upload'),
    path('documents/<int:pk>/',             views.document_detail,     name='document_detail'),
    path('documents/<int:pk>/edit/',        views.document_edit,       name='document_edit'),
    path('documents/<int:pk>/delete/',      views.document_delete,     name='document_delete'),
    path('documents/<int:pk>/download/',    views.document_download,   name='document_download'),
    path('my-documents/',                   views.my_documents,        name='my_documents'),
    path('notifications/',                  views.notifications_view,  name='notifications'),
    path('notifications/clear/',            views.clear_notifications, name='clear_notifications'),
    path('profile/',                        views.profile,             name='profile'),
    path('profile/<str:username>/',         views.public_profile,      name='public_profile'),
    path('category/<int:pk>/',              views.category_detail,     name='category_detail'),
    path('comment/<int:pk>/delete/',        views.comment_delete,      name='comment_delete'),
]
