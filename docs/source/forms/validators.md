title: Validadores
template: page.html


# Validadores

...


## Validadores predefinidos

...


## Definiendo tus propios validadores

...


## Validadores a nivel de formulario

A veces, para validar un campo, podemos necesitar compararlo con otros. No es seguro, sin embargo, que estos valores ya hayan sido procesados al momento de hacer la validación normal, de modo que necesitamos usar un tipo especial de validador.

Los validadores 'de formulario', es decir que hereden de `solution.forms.validators.FormValidator` serán procesados después que los demás, cuando los valores de todos los campos ya son conocidos.

Por ejemplo un formulario de registro podría ser como sigue:

```python
from solution import forms as f

class RegisterForm(Form):
    login = forms.TextField()
    password = forms.PasswordField()
    repeat_password = forms.PasswordField(
        validate=[
            f.AreEqual('password', 'repeat_password', 
                message=u'Passwords must match'),
        ]
    )
```

En este ejemplo, agregamos el validador a nivel de formulario `AreEqual`, para asegurarnos que el valor de `repeat_password` sea igual al de `password`.


## Definiendo un validador de formulario

...
