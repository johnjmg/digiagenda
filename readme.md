# DigiAgenda

Plataforma SaaS para microempresas de servicios: micro-sitio web, reservas en línea y valoraciones verificadas mediante token.

## Tecnologías
- Backend: Django + Django REST Framework
- Autenticación: JWT
- Base de datos: SQLite (desarrollo) / PostgreSQL (producción)
- Frontend: HTML, CSS, JavaScript vanilla
- Despliegue: PythonAnywhere

## Demo en vivo
- Micro-sitio: https://johnjmg.pythonanywhere.com/frontend/micro-sitio.html?id=1
- Dashboard: https://johnjmg.pythonanywhere.com/frontend/dashboard.html

## Instalación local
```bash
git clone https://github.com/johnjmq/digiagenda.git
cd digiagenda
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
# crear archivo .env con SECRET_KEY, DEBUG, ALLOWED_HOSTS
python manage.py migrate
python manage.py runserver