title: Validadores
template: page.html


# Validadores




## Validadores a nivel de formulario

A veces, para validar un campo, podemos necesitar compararlo con otros. No es seguro, sin embargo, que estos valores ya hayan sido procesados al momento de hacer la validación. Sin embargo, podemos solucionarlo definiendo validadores que actúen a nivel de formulario, usando el camo `_validators`.

Por ejemplo un formulario de registro podría ser como sigue:

```python
from solution.forms.validators import AssertEqual

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=True)


class RegisterForm(User.Form):
    _fields = ['login', 'password', 'repeat_password']
    _validators = [
        AssertEqual('password', 'repeat_password',
            msg=u'Passwords must match'),
    ]
```

En este ejemplo, `repeat_password` no está definido en el modelo, sino uno que solo se usa en el formulario. Por defecto no tiene ningún validador asignado. Agregamos un validador a nivel de formulario para asegurarnos que su valor sea igual al de `password`.
