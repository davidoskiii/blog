from django import forms

from .models import Post, Tag, Comment, Folder

# Classe Tailwind standard per gli input di testo e textarea
INPUT_CLASSES = (
    'w-full font-mono text-base sm:text-sm p-2.5 bg-transparent '
    'border border-gray-500 dark:border-gray-700 '
    'text-gray-800 dark:text-gray-200 '
    'placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:border-black dark:focus:border-gray-300 '
    'box-border'
)

# Variante per select / select multiple (evita sfondo bianco nativo in dark mode)
SELECT_CLASSES = (
    f'{INPUT_CLASSES} bg-white dark:bg-gray-950'
)


class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Tag",
        help_text="Tieni premuto CTRL (o CMD su Mac) per selezionare più tag.",
        widget=forms.SelectMultiple(attrs={
            'class': SELECT_CLASSES,
            'style': 'min-height: 120px;'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'tags', 'text']
        labels = {
            'title': 'Titolo',
            'text': 'Contenuto',
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


class FolderForm(forms.ModelForm):
    posts = forms.ModelMultipleChoiceField(
        queryset=Post.objects.all().order_by('-date'),
        required=False,
        label="Post nella folder",
        help_text="Tieni premuto CTRL (o CMD su Mac) per selezionare o deselezionare più post.",
        widget=forms.SelectMultiple(attrs={
            'class': SELECT_CLASSES,
            'style': 'min-height: 220px;'
        })
    )

    class Meta:
        model = Folder
        fields = ['name', 'description', 'posts']
        labels = {
            'name': 'Nome folder',
            'description': 'Descrizione',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'nome_folder...'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 3,
                'placeholder': 'descrizione_folder...'
            }),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']
        labels = {
            'name': 'Nome tag',
            'description': 'Descrizione',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'nome_tag...'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
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
                'placeholder': '// inserisci_commento...',
                'class': INPUT_CLASSES
            }),
        }
