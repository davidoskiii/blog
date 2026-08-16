from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# Stessa classe Tailwind usata per PostForm, CategoryForm e CommentForm
TAILWIND_INPUT_CLASS = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
)


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = TAILWIND_INPUT_CLASS


class CustomRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = TAILWIND_INPUT_CLASS
