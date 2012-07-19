# Changes


## 1.1.15

- An empry data value is returned as `None` instead of `u''`.
- When the forms of a FormSet have registered database objects with an `id` attribute, if no data is provided, those objects are automatically deleted at `form.save` time.

