
=======================================
Shake-SQLAlchemy
=======================================

Shake.SQLAlchemy es una lugera capa sobre SQLAlchemy, para trabajar más
comodamente con bases de datos desde tu aplicación Shake.


Declaración de una BD
=======================================

    from shake_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(SQLALCHEMY_URI)

        SQLALCHEMY_URI sigue el formato

            'motor://usuario:password@servidor:basededatos'

        (ejemplo: 'postgresql://test:test@127.0.0.1/prezentit'); o

            'sqlite:///basededatos'

        (ejemplo: 'sqlite:///db.sqlite').


Ahora `db` contiene todos los atributos y funciones definidad en los módulos
`sqlalchemy` y `sqlalchemy.orm`.


Declaración de modelos
=======================================

Ejemplo:

    from .models import db


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.String(255), unique=True,
            nullable=False)
        password = db.Column(db.String(300),
            nullable=True)
        fullname = db.Column(db.Unicode(255),
            nullable=False, default=u'')
        date_joined = db.Column(db.DateTime, default=datetime.utcnow,
            nullable=False)


Ejemplos de queries
=======================================

    SELECT * FROM TABLA;
    db.query(Tabla).all()

    SELECT a, b FROM TABLA;
    db.query(Tabla.a, Tabla.b).all()

    SELECT * FROM TABLA WHERE a = 3;
    db.query(Tabla).filter(Tabla.a == 3).all()

Nota:
    .all() para traer todos
    .first() para traer el primero


    SELECT COUNT(*) FROM TABLA WHERE a = 3;
    db.query(Tabla).filter(Tabla.a == 3).count()



JSONEncodedType
=======================================
Shake-SQLAlchemy tambien viene con una columna para guardar tipos de datos JSON,
que se encarga automaticamente de la codificacion/decodificación

    from shake_sqlalchemy import JSONEncodedType


    class MyTable(db.Model):
        data = db.Column(JSONEncodedType)
        …







