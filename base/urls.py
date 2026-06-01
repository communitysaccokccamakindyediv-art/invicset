from django.urls import path
from django.contrib.auth import views as auth_views  
from .views import (
    download_room_file, index, signup,
    login_view, logout_view,
    home, lobby, room,
    getToken, createMember, getMember, deleteMember,
    chatindex, chatroom,
    email_view,
    add_admin_staff_number,
    upload, upload_room_file, video_list, download_video,
    aboutus, contactus,
    admin_dashboard, all_answers,
    permission_denied
)

urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
    path('logout/', logout_view, name='logout'),
    path('home/', home, name='home'),
    path('lobby/', lobby, name='lobby'),
    path('room/<str:room_name>/', room, name='room'),  
    path('get_token/', getToken, name='get_token'),
    path('create_member/', createMember, name='create_member'),
    path('get_member/', getMember, name='get_member'),
    path('delete_member/', deleteMember, name='delete_member'),
    path('chatindex/', chatindex, name='chatindex'),
    path('chat/<str:room_name>/', chatroom, name='chatroom'),  # More specific pattern
    path('email/', email_view, name='email_form'),
    path('add_admin_staff_number/', add_admin_staff_number, name='add_admin_staff_number'),
    path('upload/', upload, name='upload'),
    path('videos/', video_list, name='video_list'),
    path('download-video/<int:video_id>/', download_video, name='download_video'),
    path('aboutus/', aboutus, name='aboutus'),
    path('contactus/', contactus, name='contactus'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/answer/<int:question_id>/', admin_dashboard, name='answer_question'),
    path('all_answers/', all_answers, name='all_answers'),
    path('permission_denied/', permission_denied, name='permission_denied'),

    path(
        "download-room-file/<int:file_id>/",
        download_room_file,
        name="download_room_file"
    ),

    path('room/<str:room_name>/upload-file/', upload_room_file, name='upload_room_file'),
]
