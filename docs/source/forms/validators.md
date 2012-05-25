title: Validadores
template: page.html


# Validadores

...


## Validadores a nivel de formulario

A veces, para validar un campo, podemos necesitar compararlo con otros. No es seguro, sin embargo, que estos valores ya hayan sido procesados al momento de hacer la validación. Sin embargo, podemos solucionarlo definiendo validadores que actúen a nivel de formulario, usando el camo `_validators`.

Por ejemplo un formulario de registro podría ser como sigue:

```python
from solution import Form
from solution.forms.validators import AssertEqual

class RegisterForm(Form):
    login = forms.TextField()
    password = forms.PasswordField()
    repeat_password = forms.PasswordField()

    _validate = [
        AssertEqual('password', 'repeat_password',
            message=u'Passwords must match'),
    ]
```

En este ejemplo, agregamos un validador a nivel de formulario para asegurarnos que el valor de `repeat_password` sea igual al de `password`.
