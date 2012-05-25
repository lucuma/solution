title: Campos
template: page.html


# Campos

...

<div class="note" markdown="1">
A diferencia de otras bibliotecas de manejo de formularios, _Solution_ habla de _campos_, independientemente de su representación en HTML. Por eso mismo, no hay un tipo de campo `TextArea` o `InputHidden`, si no la posibilidad de cambiar la representación de un campo de texto estándar para que se muestren de esa forma.

Los campos que si estan incluidos, como los de email y fecha, lo fueron por que añaden una comportamiento de conversión y/o validación por defecto, no solo porque su atributo `type` en el HTML es diferente. De hecho, podrías tener un `URLField` que se muestre como `<input type="hidden">`.

</div>

...