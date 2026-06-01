from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import AdminStaff, Answer, Attendee, CustomUser, AdminStaffNumber, OtherUser, Question, RoomMember
from .models import RoomFile

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'email_confirmed', 'is_other_user', 'is_admin_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('last_login',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_other_user', 'is_admin_staff')}),
        ('Email Confirmation', {'fields': ('email_confirmed',)}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Profile Picture', {'fields': ('profile_picture',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_superuser', 'email_confirmed', 'profile_picture', 'is_other_user', 'is_admin_staff')}
        ),
    )

# Register models
admin.site.register(CustomUser, CustomUserAdmin)

# Register AdminStaffNumber model
@admin.register(AdminStaffNumber)
class AdminStaffNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


admin.site.register(RoomMember)

@admin.register(OtherUser)
class OtherUserAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(AdminStaff)
class AdminStaffAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_name', 'timestamp')
    search_fields = ('user__username', 'room_name')


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1  # Number of empty forms to display

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_text', 'created_at')
    search_fields = ('question_text', 'user__username')
    list_filter = ('created_at',)
    inlines = [AnswerInline]

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created_at')
    search_fields = ('answer_text', 'user__username', 'question__question_text')
    list_filter = ('created_at',)
    raw_id_fields = ('question',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)



from django.contrib import admin
from .models import (
    ChatRoom,
    RoomParticipant,
    ChatMessage,
    MessageReaction,
    MessageRead
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'host', 'created_at')
    search_fields = ('name', 'host__username')
    list_filter = ('created_at',)


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'room',
        'user',
        'role',
        'is_online',
        'is_typing',
        'joined_at'
    )

    search_fields = (
        'room__name',
        'user__username'
    )

    list_filter = (
        'role',
        'is_online',
        'is_typing',
        'joined_at'
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'room',
        'sender',
        'message_type',
        'timestamp'
    )

    search_fields = (
        'room__name',
        'sender__username',
        'message'
    )

    list_filter = (
        'message_type',
        'timestamp'
    )


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message',
        'user',
        'emoji',
        'created_at'
    )

    search_fields = (
        'user__username',
        'emoji'
    )

    list_filter = (
        'emoji',
        'created_at'
    )


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message',
        'user',
        'read_at'
    )

    search_fields = (
        'user__username',
    )

    list_filter = (
        'read_at',
    )
    
@admin.register(RoomFile)
class RoomFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "original_name",
        "room",
        "uploaded_by",
        "uploaded_at",
    )

    list_filter = (
        "uploaded_at",
        "room",
    )

    search_fields = (
        "original_name",
        "uploaded_by__username",
        "room__name",
    )

    readonly_fields = (
        "uploaded_at",
    )

    ordering = ("-uploaded_at",)