title: Formularios a partir de modelos
template: page.html


# Formularios a partir de modelos

Aunque pueden armarse formularios desde cero, la mayoría de las veces se usan para editar un modelo ya existente. En vez de repetir los campos en el modelo y en el formulario, ¿no sería mucho más fácil si pudieramos simplemente reusarlos? Por suerte, _Solution_ te permite hacer jústamente eso.

Cada modelo tiene como atributo una clase `Form` que puede heredarse para generar un nuevo formulario.

Por ejemplo, si nuestra aplicación tiene los siguientes modelos:

```python
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    published_at = db.Column(db.Date)
    author = db.relationship('Author', 
        backref=db.backref('books', lazy='dynamic'))
```

```python
class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200), default=u'')
```

para crear un formulario, basta hacer

```python
class PostForm(Post.Form):
    _fields = ['title', 'content', 'published_at', 'author',]
```

Solamente para los campos del modelo listados en `_fields`, _Solution_ crea automáticamente campos en el formulario (también, por seguridad, serán los únicos procesados).

Un formulario creado de esta manera se usa y comporta de la misma forma que uno definido a mano, con una diferencia: el método `save`, no necesita de ningúna argumento, sino que actualiza la información de su objeto asociado diréctamente.

```python
def update_post(request, book_id):
    form = PostForm(request)
    if form.is_valid():
        form.save()
        db.commit()
        return redirect('/')
    return render('posts/edit.html', locals())
```

## Validadores de campos

...




## Asociaciones

Para usar modelos relacionados —como el de `post.author` en el primer ejemplo— _Solution_ puede generar `<select>` o una serie de botones de radio o checks, llenándolos con la lista de objetos de dicho modelo. Veamos como funciona.

```jinja
<label>Author</label>
{{ form.author('name') }}
```

se mostrará como:

-----> IMAGEN1 <------

Puedes personalizar esta lita, filtar estos valores u ordenarlos de otro modo, diréctamente al mostrarlos

```jinja
<label>Author</label>
{{ form.author('name').filter_by(deleted=False) }}
```

o al definir el formulario

```python
class PostForm(Post.Form):
    _fields = ['title', 'content', 'published_at', 'author',]

    author = {
        'collection': db.query(Author.name).filter_by(deleted=False)
    }
```

