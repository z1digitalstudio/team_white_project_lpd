# 📰 1710-CMS (Django Blog CMS)

Este proyecto es un **CMS (Content Management System)** desarrollado con Django.  
Permite a cada usuario tener su propio blog, crear publicaciones con un editor enriquecido (TinyMCE), subir imágenes, asignar etiquetas y gestionarlas desde el panel de administración.

---

## ⚙️ **Instalación y ejecución local**

<details>
  <summary><strong>Guía clásica (entorno virtual)</strong></summary>

1️⃣ Clonar el repositorio  
```bash
git clone https://github.com/luisparadela-z1/1710-cms.git
cd 1710-cms/mysite
```

2️⃣ Activar el entorno virtual  
```bash
python3 -m venv ../venv
source ../venv/bin/activate
```

3️⃣ Instalar dependencias  
```bash
pip install -r requirements.txt
```

4️⃣ Aplicar migraciones  
```bash
python manage.py migrate
```

5️⃣ Crear superusuario (si no lo has hecho)  
```bash
python manage.py createsuperuser
```

6️⃣ Ejecutar el servidor de desarrollo  
```bash
python manage.py runserver
```

7️⃣ Accede desde el navegador  
- **Admin:** http://127.0.0.1:8000/admin/  
- **Blog público:** http://127.0.0.1:8000/blog/

</details>

---

<details>
  <summary><strong>Ejecutar con Docker (recomendado para producción/desarrollo rápido)</strong></summary>

Asegúrate de tener [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/) instalados.

1️⃣ Clonar el repositorio  
```bash
git clone https://github.com/luisparadela-z1/1710-cms.git
cd 1710-cms
```

2️⃣ Crea o revisa los archivos `Dockerfile` y `docker-compose.yml` (proporcionados en el repo). Si no existen, deberías crearlos como sigue:

**Ejemplo mínimo de Dockerfile:**
```Dockerfile
FROM python:3.12
WORKDIR /app
COPY mysite/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY mysite /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**Ejemplo mínimo de docker-compose.yml:**
```yaml
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mysite
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  web:
    build: .
    command: bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./mysite:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_NAME: mysite
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_HOST: db
      DB_PORT: 5432
volumes:
  postgres_data:
```

3️⃣ Construye y lanza los contenedores  
```bash
docker compose up --build
```

4️⃣ Crea el superusuario (en otra terminal):  
```bash
docker compose exec web python manage.py createsuperuser
```

5️⃣ Accede desde el navegador  
- **Admin:** http://localhost:8000/admin/  
- **Blog:** http://localhost:8000/blog/

> **Nota:** Si quieres ejecutar comandos adicionales, solo usa  
> `docker compose exec web <comando>`  
> Ejemplo:  
> `docker compose exec web python manage.py shell`

</details>

---

## 📦 Estructura del proyecto

```
1710-cms/
│
├── mysite/
│   ├── mysite/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── core/
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       └── core/
│   │           ├── post_list.html
│   │           └── post_detail.html
│   │
│   ├── manage.py
│
├── venv/           # solo en desarrollo local
│
└── README.md
```

---

## 📚 Dependencias principales

Archivo requirements.txt recomendado:

```
Django>=5.2
django-tinymce>=4.0
django-import-export>=4.0
Pillow>=10.0
```

Instálalas con:

```bash
pip install -r requirements.txt
```

---

## 🧭 Funcionalidades disponibles

| Funcionalidad                      | Estado | Descripción                          |
| -----------------------------------|:------:|--------------------------------------|
| Crear Blogs por usuario            |   ✅   | Cada usuario tiene un blog propio    |
| Crear Posts con editor TinyMCE     |   ✅   | Editor enriquecido                   |
| Añadir etiquetas                   |   ✅   | Sistema de tags reutilizables        |
| Subir imágenes (cover)             |   ✅   | Campo cover en los posts             |
| Filtrar y buscar en admin          |   ✅   | Listados personalizados              |
| Mostrar posts publicados           |   ✅   | Listado en /blog/                    |
| Detalle del post                   |   ✅   | Vista /blog/&lt;slug&gt;/            |
| Control de visibilidad por usuario |   ✅   | Cada usuario ve solo su blog         |

---

## 🔮 Roadmap

### Fase 2 – Mejoras del blog público

- [ ] Añadir paginación al listado de posts
- [ ] Mostrar imagen de portada (cover) en post_list.html
- [ ] Mostrar etiquetas y autor en post_detail.html
- [ ] Añadir sistema de comentarios

### Fase 3 – Autenticación y dashboards

- [ ] Permitir registro y login desde el frontend
- [ ] Dashboard de usuario fuera del admin
- [ ] Perfil público (`/user/<username>/`)

### Fase 4 – Diseño y estilo

- [ ] Crear plantilla base (`base.html`)
- [ ] Integrar TailwindCSS o Bootstrap
- [ ] Añadir cabecera, footer y navegación responsive

### Fase 5 – API y despliegue

- [ ] Implementar API REST con Django REST Framework
- [ ] Preparar para despliegue en Render / Railway / Vercel

---

## 🌿 GitFlow - Flujo de trabajo

Este proyecto sigue el flujo de trabajo **GitFlow** para mantener un historial de commits organizado y facilitar la colaboración.

### Ramas principales

- **`main`**: Rama de producción. Solo recibe código estable mediante releases.
- **`develop`**: Rama de desarrollo. Contiene el código más reciente y estable para desarrollo.

### Flujo de trabajo

#### 1. Crear una nueva feature

```bash
# Asegúrate de estar en develop y actualizado
git checkout develop
git pull origin develop

# Crea una nueva rama feature
git checkout -b feature/nombre-de-la-feature

# Trabaja en tu feature, haz commits...
git add .
git commit -m "feat: descripción del cambio"

# Sube la rama
git push origin feature/nombre-de-la-feature
```

#### 2. Crear Pull Request

1. Ve a GitHub y crea una **Pull Request** desde `feature/nombre-de-la-feature` hacia `develop`.
2. Completa el template de PR con:
   - Ticket/Issue relacionado
   - Descripción de los cambios
   - Plan de testing
3. Asigna reviewers si es necesario.

#### 3. Mergear a develop

- **Usa SQUASH** al mergear feature branches a `develop`.
- Esto mantiene el historial limpio con un solo commit por feature.

#### 4. Release a main

Cuando `develop` esté listo para producción:

```bash
# Crear rama release (opcional) o mergear directamente
git checkout main
git pull origin main
git merge develop  # Usa MERGE COMMIT (no squash)
git push origin main
```

### Convenciones de commits

Seguimos **Conventional Commits**:

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `refactor:` Refactorización de código
- `docs:` Cambios en documentación
- `test:` Añadir o modificar tests
- `chore:` Tareas de mantenimiento

**Ejemplo:**
```bash
git commit -m "feat: add user registration endpoint"
git commit -m "fix: resolve 500 error on blog creation"
```

### Referencias

- [GitFlow Cheat Sheet](https://danielkummer.github.io/git-flow-cheatsheet/index.es_ES.html)
- [Git Rebase vs Merge vs Squash](https://dev.to/devsatasurion/git-rebase-vs-merge-vs-squash-how-to-choose-the-right-one-3a33)

---

## 💡 Autor

**👤 Luis Paradela**  
[GitHub: luisparadela-z1](https://github.com/luisparadela-z1)

---
