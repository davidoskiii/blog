from django import forms 

from .models import Post, Category, Comment

# Classe Tailwind standard per gli input di testo e select
INPUT_CLASSES = (
    'w-full font-mono text-sm p-2 bg-transparent border border-gray-600 '
    'text-gray-800 placeholder-gray-400 focus:outline-none focus:border-black'
)

class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="[VARIE]",
        label="// CATEGORIA",
        widget=forms.Select(attrs={
            'class': INPUT_CLASSES
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'category', 'text']
        labels = {
            'title': '// TITOLO',
            'category': '// CATEGORIA',
            'text': '// CONTENUTO_POST',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'inserisci_titolo...'
            }),
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': INPUT_CLASSES,
                'placeholder': 'scrivi_contenuto...'
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': '// NOME_CATEGORIA'}
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'es_tecnologia...'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': "// inserisci_commento...",
                'class': INPUT_CLASSES
            }),
        }
