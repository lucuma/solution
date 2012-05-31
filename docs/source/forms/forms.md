title: Formularios
template: page.html


# Formularios

Una pieza clave de una aplicación web es obtener información del usuario. La forma común de hacer esto es a través de un formulario.

Los formularios están por todos lados, aunque no lo parezcan: en la búsqueda, registro, ingreso, etc. Pero programar los formularios puede ser una fuente de frustración. Estos deben:

* Pedirle al usuario alguna información, quizas dándole a elegir entre las opciones disponibles para algunos campos.
* Validar a conciencia esta información y luego convertirla a un tipo de datos apropiado (por ejemplo el texto `'05/05/2012'` a un `datetime` de Python).
* Si el usuario ha cometido algún error, mostrar un mensaje informativo.
Además los campos deben mostrarse con su contenido original, para evitar que tenga que llenarlos de nuevo.

Aunque se puede generar, validar y procesar la información de un formulario a mano, ¡es mucho trabajo!

Por suerte, el sistema de formularios de _Solution_ se encarga de hacer la mayoría del trabajo por tí. Tu le das una descripción de los campos del formulario, reglas de validación y una plantilla simple, y *Solution* hace el resto por ti. El resultado es un “formulario perfecto” con muy poco esfuerzo.



