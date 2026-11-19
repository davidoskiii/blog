from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

INPUT_CLASSES = (
    'w-full font-mono text-base sm:text-sm p-2.5 bg-transparent '
    'border border-gray-500 dark:border-gray-700 '
    'text-gray-800 dark:text-gray-200 '
    'placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:border-black dark:focus:border-gray-300 '
    'box-border'
)


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASSES


class CustomRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASSES
