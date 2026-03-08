from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Document, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def _add_class(self, field_name):
        self.fields[field_name].widget.attrs.update({'class': 'form-input'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder']    = 'your@email.com'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username', 'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model   = Document
        fields  = ['title', 'category', 'description', 'file']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Python Study Notes'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe this document...'}),
            'file':        forms.ClearableFileInput(attrs={'class': 'file-input', 'id': 'fileInput'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError('File must be under 20 MB.')
            ext = file.name.rsplit('.', 1)[-1].lower()
            allowed = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
            if ext not in allowed:
                raise forms.ValidationError(f'File type .{ext} not allowed. Use: PDF, Word, Excel, PowerPoint, TXT.')
        return file


class DocumentEditForm(forms.ModelForm):
    class Meta:
        model   = Document
        fields  = ['title', 'category', 'description', 'file']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-input'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'file':        forms.ClearableFileInput(attrs={'class': 'file-input', 'id': 'fileInput'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model   = Comment
        fields  = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }
        labels = {'content': ''}


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-input'}),
            'email':      forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
