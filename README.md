# Proyecto Etapa1 CI-3725-Traductores e Interpretadores
##lexer.py
-Recibe como entrada un archivo .imperat en la llamada al programa como argumento:
python lexer.py prueba.imperat

-Analisador de caracteres, revisa todos los caracateres dentro del archivo correspondinete.

-Reporta que tipo de token se genera junto con su posición vertical y horizontal.

-Reporta errores cuando detecta un caracter que no está definido para el lenguaje

##run_tests.py

-Este algoritmo se encarga de ejecutar lexer.py con cada caso de prueba y 
comparar la salida con la salida esperada en otro archivo salida.out

-Los casos de prueba deben estar en una carpeta llamada TestCases en el mismo
nivel donde se encuentrar los algoritmos .py

-Dentro de esta carpeta deben encontrarse dos rutas, Tests y Outs que contienen
los casos de prueba y las salidas esperadas respectivamente.

-El algoritmo compara la salida de lexer.py con cada caso prueba.imperat contra
salida.out y determina si concuerda o no.
