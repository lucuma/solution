title: Guia rápida
template: page.html


# Guia rápida


Esta página es una guía rápida de como usar **_Solution_** en tus aplicaciones. Para tener una visión completa, no dejes de revisar el resto de la documentación y la nativa de [SQLAlchemy](http://docs.sqlalchemy.org/en/latest/orm/).


## Conectándose a una base de datos

Para el caso común de una base de datos en un solo lugar, todo lo que tienes que hacer es crear un objeto `SQLAlchemy` pasándole la ruta correcta.

```python
import solution
db = solution.SQLAlchemy(SQLALCHEMY_URI)
```

`SQLALCHEMY_URI` sigue uno de estos formatos:

    motor://usuario:password@servidor:basededatos
    sqlite:///basededatos

Por ejemplo: `'postgresql://test:test@127.0.0.1/prezentit'` o `'sqlite:///db.sqlite'`.

<aside class="info" markdown="1">
El segundo caso usa `sqlite`, un motor de base de datos que posíblemente ya venga instalado en tu máquina, más que suficiente para hacer pruebas. Para usos reales —es decir más de una persona a la vez— deberías hacer algo como el primer caso.
</aside>


### Usándola con Shake

Para usarla en una aplicación web hecha con `Shake` debes pasarle la instancia como segundo argumento:

```python
form shake import Shake
import solution

app = Shake()
db = solution.SQLAlchemy(SQLALCHEMY_URI, app=app)
```

o luego de creada:

```python
db = solution.SQLAlchemy(SQLALCHEMY_URI)
db.init_app(app)
```


## Declarando modelos

`db` contiene todos los atributos y funciones definidas en los módulos `sqlalchemy` y `sqlalchemy.orm`. Además, provee una clase llamada `Model` que es la base declarativa que usaremos al declarar nuestros modelos.

```python
class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(300), nullable=True)

    def __init__(self, login, email):
        self.login = login
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.login
```

Para generar esta tabla (y cualquier otra) en la base de datos, basta con hacer:

```python
db.create_all()
```

¡Listo! Ahora, creemos algunos usuarios

```python
from main import db
from models import User

admin = User('admin', 'admin@example.com')
guest = User('guest', 'guest@example.com')
```

pero aún no están en la base de datos, así que agreguémoslos

```python
db.add(admin)
db.add(guest)
db.commit()
```

## Leyendo datos

Acceder a lo guardado en la base de datos es increiblemente simple

```python
>>> users = User.query.all()
[<User u'admin'>, <User u'guest'>]
>>> admin = User.query.filter(User.login='admin').first()
<User u'admin'>
```

Otros ejemplos:

```python
# SELECT a, b FROM users;
db.query(Modelo.a, Modelo.b).all()

# SELECT * FROM Tabla WHERE a = 3;
db.query(Modelo).filter(Modelo.a == 3).all()
db.query(Modelo).filter(Modelo.a == 3).first()

# SELECT COUNT(*) FROM Tabla WHERE a = 3;
db.query(Modelo).filter(Modelo.a == 3).count()
```

## Relaciones entre tablas

SQLAlchemy trabaja con bases de datos relacionales. Y lo que hacen mejor las bases de datos relacionales son *relaciones* entre tablas. Veamos un ejemplo de eso:

```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name
```
```python
class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User',
        backref=db.backref('addresses', lazy='dynamic'))

    def __init__(self, email, user=None):
        self.email = email
        if user:
            self.user = user

    def __repr__(self):
        return '<Address %r>' % self.email
```
```python
db.create_all()
```

Primero creemos algunos objetos:

```python
user = User('Jane Doe')
a1 = Address('jane@example.com', user)
a2 = Address('jdoe@example.org', user)
db.add(user)
db.add(a1)
db.add(a2)
```

Ahora, como declaramos `addresses` como una relación dinámica (`lazy='dynamic'`), este campo se muestra como un query: 

```python
>>> user.addresses
<sqlalchemy.orm.dynamic.AppenderQuery at 0x101d47a10>
```

Se porta como una query regular también, de modo que podemos pedirles todos los autores o filtrar u ordenar esa lista.

```python
>>> user.addresses.all()
[<Address 'jane@example.com'>, <Address 'jdoe@example.org'>]
```

Finalmente, los grabamos en la base de datos haciendo: 

```python
db.commit()
```

## Diferencias con SQLALchemy

Las únicas cosas que necesitas saber de **_Solution_**, comparado con SQLAlchemy a secas son:

1.  La clase `solution.SQLAlchemy` te da acceso a lo siguiente:

    - todas las funciones y clases de `sqlalchemy` y `sqlalchemy.orm`.
    - una sesion pre-configurada llamada `session`.
    - el atributo `query`, para hacer consultas a la base de datos.
    - el atributo `~SQLAlchemy.metadata`
    - el atributo `~SQLAlchemy.engine`
    - los métodos `create_all` y `drop_all`, que llaman para crear y borrar tablas, deacuerdo a los modelos.
    - una serie de métodos que apuntan a los de la sesión: `create_all`, `drop_all`, `add`, `flush`, `commit` y `rollback`.
    - una clase `Model` de la cual heredamos nuestros modelos.

2.  La clase base declarativa `Model` se porta como una clase regular de Python, solo que todas las clases que hereden de ella serán consideradas modelos.
    También, provee los métodos `to_dict` y `to_json` par serializar una un objeto (una fila de la tabla).

3.  La clase `Query`, instanciada cuando haces `db.query(Modelo)`, además de los métodos estándar de una query de SQLAlchemy, añade los métodos `first_or_notfound` y `get_or_notfound`. Estos son como `first` y `get`, solo que lanzan una excepción `NotFound` si no encuentran ningún resultado.

4.  Tienes siempre que hacer `db.commit()` pero si inicializas la clase `solution.SQLAlchemy` con una instancia de `Shake` o `Flask` como segundo argumento, no es necesario que la destruyas al final del request. _Solution_ lo hace por ti.

5. _Solution_ incluye un tipo de columna para guardar diccionarios de Python serializándolos a JSON.

```python
from solution import JSONEncodedType

class MyTable(db.Model):
    data = db.Column(JSONEncodedType, nullable=False)
    ...
```


