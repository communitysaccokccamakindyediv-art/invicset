from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Answer, Attendee, CustomUser, AdminStaffNumber, Question

User = get_user_model()

# Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    user_type = forms.ChoiceField(choices=[('otheruser', 'Other User'), ('adminstaff', 'Admin Staff')], label='User Type')
    admin_staff_number = forms.CharField(label='Admin Staff Number', required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2', 'profile_picture', 'user_type', 'admin_staff_number')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_admin_staff_number(self):
        user_type = self.cleaned_data.get('user_type')
        admin_staff_number = self.cleaned_data.get('admin_staff_number')

        if user_type == 'adminstaff':
            if not admin_staff_number:
                raise forms.ValidationError("Admin Staff Number is required for Admin Staff.")
            if not AdminStaffNumber.objects.filter(number=admin_staff_number).exists():
                raise forms.ValidationError("Invalid Admin Staff Number.")
        return admin_staff_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'otheruser':
            user.is_other_user = True
        elif user_type == 'adminstaff':
            user.is_admin_staff = True
        if commit:
            user.save()
        return user

# LOGIN FORM
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('otheruser', 'Other User'), ('adminstaff', 'Admin Staff')], label='User Type')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add any email validation logic here if needed
        return email

# USER MODEL
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

# PASSWORD RESET FORM
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')


class EmailForm(forms.Form):

    email1 = forms.EmailField(
        label='Email 1',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'REQUIRED !'
        })
    )

    email2 = forms.EmailField(
        label='Email 2',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional'
        })
    )

    email3 = forms.EmailField(
        label='Email 3',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional'
        })
    )

    chat_name = forms.CharField(
        label='Chat Name',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control hidden',
            'placeholder': 'Chat Name'
        })
    )

    conference_name = forms.CharField(
        label='Conference Name',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control hidden',
            'placeholder': 'Conference Name'
        })
    )

    rules = forms.CharField(
        label='Rules',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control hidden',
            'rows': 4,
            'placeholder': 'Schedule Date & Time'
        })
    )


class AdminStaffNumberForm(forms.ModelForm):
    class Meta:
        model = AdminStaffNumber
        fields = ['number']



class AttendeeForm(forms.ModelForm):
    room_name = forms.CharField(max_length=255, required=True, label='Room Name')

    class Meta:
        model = Attendee
        fields = ['recorded_video', 'room_name']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

        widgets = {
            'question_text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Type your support request here...',
                'class': 'form-control',
            })
        }

        labels = {
            'question_text': 'Your Question:'
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Type your answer here...'}),
        }

