Manual de Instalación


Requisitos del Sistema
Sistema Operativo: Windows o Linux.
Git: Para clonar el repositorio.
Si va a realizar la instalación en su máquina local:
Python: Versión 3.10+ (recomendada: 3.11.2)
Node.js 18+ y npm.
Si va a usar Docker para instalar la aplicación:
Docker Desktop: versión 4.7+ (recomendado)
Docker Compose: incluido con Docker Desktop.
No es necesario instalar manualmente las aplicaciones mencionadas en la sección de
local, ya que las imágenes Docker incluyen todas las dependencias necesarias.


Guía de Instalación con Docker

Clonar el repositorio
git clone https://github.com/Jechig0/TFG.git
cd TFG

Instalar Docker Desktop y Docker Compose
Descargue Docker Desktop desde la https://www.docker.com/products/docker-desktop,
seleccionando para su equipo la versión correspondiente.
Tras la instalación, verifique que tiene tanto docker como docker compose:
docker --version
docker compose version
Docker Desktop incluye Docker Compose por lo general, pero si por algún motivo Docker
Compose no le aparece instalado, siga las instrucciones del sitio web oficial
https://docs.docker.com/compose/install.

Construir los contenedores y levantar
Con Docker Desktop ejecutandose, compile todas las imágenes y levantelas:
docker compose build --no-cache
docker compose up -d
La flag --no-cache no es obligatoria, sirve para reconstruir los contenedores de cero, sin usar
nada que esté previamente almacenado en la memoria. Esto es útil por si realiza modificaciones
en el código del proyecto, para asegurarse que al reconstruir las imágenes se implementen los
cambios.
Una vez los contenedores estén construidos y ejecutandose, puede acceder al frontend des-
de http://localhost:4200, y a la documentación en Swagger del backend desde http://localhost:8000
IMPORTANTE: Las imágenes Docker pueden acabar siendo pesadas y ocupar mucho es-
pacio en memoria, si fuera necesario puede configurar desde los ajustes de Docker Desktop,
sección Resources, donde se almacenan dichas imágenes.

Bajar los contenedores (sin borrar volúmenes)
Para dejar de ejecutar la aplicación sin borrar el contenido de Docker:
docker compose down

Limpiar al completo (elimina volumenes e imágenes locales)
Para eliminar por completo el contenido de Docker para liberar capacidad:
docker compose down --volumes --rmi all


Guía de Instalación en equipo local

Clonar el repositorio
git clone https://github.com/Jechig0/TFG.git
cd TFG

Instalar Python y pip
Windows:
Descargar la versión de Python 3.11.2
Añadir Python al PATH durante la instalación.
Linux: Abrir una terminal y ejecutar (con la versión de Python descargada):
sudo apt update
sudo apt install python3 python3-pip

Configuración del entorno Python
Opcional: si no quieres modificar las librerías de Python del equipo, se recomienda crear
un entorno virtual.
python -m venv venv
Activar el entorno virtual (opcional):
Windows:
venv\Scripts\activate
Linux:
source venv/bin/activate
Instalar dependencias del Backend e iniciar

Instalar las librerías requeridas de Python. En caso de error, revisar la versión de pip y
Python, y volver a ejecutar el comando, o ejecutar el comando ‘pip install‘ para cada una de
las librerías.
pip install -r requirements.txt
Ejecutar el servidor del backend. Desde la carpeta raíz del repositorio:
cd backend
uvicorn app.main:app --reload

Instalar dependencias del Frontend y desplegar
Navegar a la carpeta de frontend. Desde la carpeta raíz del repositorio:
cd frontend
Instalar Node.js y npm. Instalar las dependencias del frontend:
npm install
Desplegar el frontend en producción:
ng serve
Acceder a la aplicación
La aplicación estará disponible en:
http://localhost:4200