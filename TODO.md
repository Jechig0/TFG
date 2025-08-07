# TODO DEL TFG

-Notas de las reuniones sobre el TFG para anotar los elementos prioritarios.

GENERAL
-Funcionalidades básicas funcionales en general, trabajar en control de errores, excepciones y posible persistencia de datos entre sesiones y problemas de concurrencia.
-Añadir filtrado para las tablas de búsqueda de asignaturas para que solo muestren las que sean optativas
-Avanzar la memoria

FRONTEND
-Trabajar creación manual de alumnos (notas manuales)
-Para alumno nuevo: si hay ya notas en el backend, que se muestren correctamente
-Añadir almacenamiento en caché para no tener que pedir otra vez el pdf al recargar.

BACKEND
-Arreglar lectura PDF (falla si una asignatura tiene calificaciones en dos páginas distintas)
-Optimizar rendimiento de endpoint probabilidadAcceso.
-Revisar precisión endpoint afinidad.
-Revisar excepciones endpoints probabilidadAcceso y afinidad.
-Trabajar muestras de precisión del cluster

REUNION
-Protección de datos con últimos digitos del DNI.
-Mensaje error: "No existen datos históricos de calificación de esta asignatura" para asignaturas recién ofertadas.
-Boton borrado de datos.
-Dashboard administrador.
-Apendices: Manual de instalación y manual de usuario.
-Para el admin dashboard: titulación que más solicita, asignatura más consultada, asignatura con afinidades más altas, asignatura con mayor probabilidad de acceso.
