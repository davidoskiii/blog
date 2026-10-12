from django import forms 

from .models import Post, Tag, Comment

# Classe Tailwind standard per gli input di testo e select
INPUT_CLASSES = (
    'w-full font-mono text-sm p-2 bg-transparent border border-gray-600 '
    'text-gray-800 placeholder-gray-400 focus:outline-none focus:border-black'
)

class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="// TAG",
        help_text="Tieni premuto CTRL (o CMD su Mac) per selezionare più tag.",
        widget=forms.SelectMultiple(attrs={
            'class': INPUT_CLASSES,
            'style': 'min-height: 120px;'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'tags', 'text']
        labels = {
            'title': '// TITOLO',
            'text': '// CONTENUTO_POST',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'inserisci_titolo...'
            }),
            'text': forms.Textarea(attrs={
                'rows': 12,
                'class': INPUT_CLASSES,
                'placeholder': 'scrivi_contenuto...'
            }),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']
        labels = {
            'name': '// NOME',
            'description': '// DESCRIZIONE',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-600 bg-transparent text-sm text-gray-800 focus:outline-none focus:border-black',
                'placeholder': 'nome_tag...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-600 bg-transparent text-sm text-gray-800 focus:outline-none focus:border-black',
                'rows': 3,
                'placeholder': 'descrizione_tag...'
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
