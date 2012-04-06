
Solution
====================

Makes SQLAlchemy easy and fun to use, and adds some custom capabilities.

Example::

.. sourcecode:: python

    from solution import SQLALchemy

    db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
            default=datetime.utcnow)

    to_do = ToDo(title='Install Solution', done=True)
    db.add(to_do)
    db.commit()

    completed = db.query(ToDo).filter(ToDo.done == True).all()

It does an automatic table naming (if no name is defined) and, to the base query class, adds the following methods::
    
    - first_or_notfound
    - get_or_notfound
    - to_json
