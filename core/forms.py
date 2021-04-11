from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment, Review
from django.forms import ModelForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name",
                  "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = user.email

        if commit:
            user.save()
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'content')

        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name', 'required': ''}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email', 'required': ''}),
            'content': forms.Textarea(attrs={'placeholder': 'Your Comment', 'required': ''})
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rate', 'review')


class ContactForm(forms.Form):
    your_name = forms.CharField()
    your_email = forms.EmailField()
    your_subject = forms.CharField()
    your_message = forms.CharField(widget=forms.Textarea)
