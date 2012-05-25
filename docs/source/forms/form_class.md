title: Clase Form
template: page.html


# Clase Form

Para definir un formulario basta declarar una clase que herede de `Form`. Cada campo está definido con un tipo de clase `Field` como atributo de la clase `Form`.

```python
from solution import forms

class MyForm(forms.Form):
    field_name = forms.FieldType(option1, option2, ...
        validate=[field_validator1, field_validator2, ... ]
    )
    ...
    _validate = [form_validator1, form_validator2, ... ]
```

Por ejemplo, un clásico formulario de “contáctanos” en una página podría ser:

```python
from solution import forms

class ContactForm(forms.Form):
    subject = forms.TextField()
    email = forms.EmailField(required=False)
    message = forms.TextField()
```

Aquí solo se usan dos `TextField` y un `EmailField`; puedes ver una lista completa de los tipos disponibles [en esta página](/forms/fields.md).

<div class="note" markdown="1">
Si vas a a usar un formulario para editar un modelo, puedes crear [formularios a partir de modelos](/forms/model_forms.md) para ahorrate el trabajo de repetir la lista de campos.
</div>

Los nombres de campos pueden ser cualquier identificador válido de Python, salvo que no pueden empezar con “_” (guión bajo). Por defecto todos son obligatorios, asi que especifiamos `require=False` para hacer opcional el campo `email`.

Cada campo puede tener un argumento `validate` con una lista de funciones de validación. El formulario también tiene un campo `_validate` para listar validadores que prueben relaciones entre varios campos. Puedes leer más en la sección de [validadores](/forms/validators.md).


## Usando un formulario en un controlador

El patrón estándar para procesar un formulario se ve así:

```python
def contact(request):
    form = ContactForm(request)

    # If the form has been submitted and all validation rules pass
    if request.is_post and form.is_valid():
        # Process the data in form.cleaned_data
        # ...
        return redirect('/thanks/') # Redirect after POST
    
    # The form is empty or has errors
    return render('contact.html', locals())
```

Hay tres posibles rutas en este código:

1. Si el formulario no ha sido enviado, una instancia vacía de ContactForm es creada y pasada a la plantilla.
2. Si el formulario ha sido enviado, `request` contendrá la información. Si esta es válida, es procesada y al usuario se le redirige a una página de “gracias”.
3. Si el formulario ha sido enviado pero es inválido, la instancia llena de ContactForm es pasada a la plantilla.

Al instanciar un formulario se le puede pasar dos argumentos opcionales con datos:

* el primero contiene los valores proporcionados por el usuario. Este puede ser un un objeto `request` o un diccionario.
* el segundo le da los valores *iniciales* del formulario y puede ser un diccionario o la instancia de un modelo.

Al mostar un formulario, entonces, _Solution_ intentará obtener un valor de uno de estas dos fuentes (en orden) y si no mostrará el campo vacío.


## Mostrando un formulario en una plantilla

_Solution_ no se mete en como diseñas tus formularios, solo te ayuda a llenarlo de valores. Por ello únicamente genera los campos necesarios y no la estructura alrededor.

![Simple form](/forms/simpleform.png){.pull-left}

```html
<form action="/contact/" method="post">
  {{ form._errors }}
  <fieldset>
    <label>Subject</label>
    {{ form.subject }}
    {{ form.subject.errors }}
  </fieldset>
  <fieldset>
    <label>E-mail</label>
    {{ form.email }}
    {{ form.email.errors }}
  </fieldset>
  <fieldset>
    <label>Message</label>
    {{ form.message.as_textarea }}
    {{ form.message.errors }}
  </fieldset>
  <fieldset class="form-actions">
    <button type="submit">Send message</button>
  </fieldset>
</form>
```

### Campos

El HTML por defecto de cada campo depende de su tipo declarado, pero también puede modificarse. Por ejemplo, un `TextField` se muestra por defecto como un `<input>`, pero puede forzarse a mostarse como un `<textarea>` símplemente agregando `as_textarea`, como en el ejemplo.

Además, los atributos de estas elementos, como `class`, `type` o cualquier otro, pueden personalizarse también, pasándolos como argumentos al reproducir los campos.

<aside class='pull-left' markdown='1'>
Para definir atributos con guiones “-”, pásalos con guiones bajos en vez “_”.
</aside>

```python
>>> f = ContactForm()
>>> f.subject
'<input type="text" name="subject">'
>>> f.email(classes='col12', data_provide="typeahead")
'<input type="email" name="email" class="col12" data-provide="typeahead">'
>>> f.message.value = 'Hello world!'
>>> f.message.as_textarea(classes='xlarge col12')
'<textarea name="message" class="xlarge col12">Hello world!</textarea>'
```

Si por algún motivo necesitas insertar en la página solo el valor actual de algún campo específico, puedes usar `form.nombre_del_campo.value`. También puedes iterar la lista de campos usando `form._fields`.

```html
<form action="/contact/" method="post">
  <fieldset>
  {{ form._errors }}
  {% for field in form._fields %}
    {{ field }}
  {% endfor %}
  </fieldset>
  <fieldset class="form-actions">
    <button type="submit">Send message</button>
  </fieldset>
</form>
```


### Errores

Si el contenido de un campo, tal como lo ha llenado un usuario, no cumple con alguna regla de validación —por ejemplo, el campo es obligarorio pero está vacío— este tendrá un error asociado a él. Por ejemplo: 

```python
>>> form.email.errors
'<span class="error">This field is required</span>''
```

La reproducción por defecto es un  `<span class="error">` con el mensaje del validador (si no has definido ningún validador o no has especificado un mensaje, se usan los mensajes por defecto). Puedes personalizar este código y/o usar el tipo de error, de manera similar a esta:

```html
<p class="{{ error.type }}">{{ error.message }}</p>
```

generará

```html
<p class="empty">This field is required</p>
```


## Procesando los datos de un formulario

Once is_valid() returns True, you can process the form submission safe in the knowledge that it conforms to the validation rules defined by your form. While you could access request.POST directly at this point, it is better to access form.cleaned_data. This data has not only been validated but will also be converted in to the relevant Python types for you. In the above example, cc_myself will be a boolean value. Likewise, fields such as IntegerField and FloatField convert values to a Python int and float respectively. Note that read-only fields are not available in form.cleaned_data (and setting a value in a custom clean() method won't have any effect) because these fields are displayed as text rather than as input elements, and thus are not posted back to the server.

Extendiendo el ejemplo anterior, así es como este formulario de conacto podria procesarse:

```python
def contact(request):
    form = ContactForm(request)

    # If the form has been submitted and all validation rules pass
    if request.is_post and form.is_valid():
        subject = form.cleaned_data['subject']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        
        recipients = ['info@example.com']
        send_mail(subject, message, sender, recipients)
        return redirect('/thanks/') # Redirect after POST
    
    # The form is empty or has errors
    return render('contact.html', locals())
```


