# 🚀 Django Production Deployment (Ubuntu + Gunicorn + Nginx + PostgreSQL)

This README is the **battle‑tested checklist** to deploy Django apps to production **without pain**.
Follow it step‑by‑step and you won’t relive this suffering again.

---

## 🧠 Architecture (Understand This First)

```
User → Nginx → Gunicorn (venv) → Django → PostgreSQL
```

* **Nginx**: Handles HTTP, HTTPS, static files
* **Gunicorn**: Runs Django
* **venv**: Isolated Python environment (mandatory)
* **PostgreSQL**: Database
* **systemd**: Keeps Gunicorn alive

---

## 1️⃣ Server Basics (Ubuntu 22/24)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip nginx git -y
```

Create non‑root user:

```bash
adduser maishaapp
usermod -aG sudo maishaapp
```

---

## 2️⃣ Project Folder Structure (DO NOT DEVIATE)

```
/home/maishaapp/apps/
 ├── main_website/
 │   ├── venv/
 │   ├── manage.py
 │   ├── <project_name>/
 │   ├── staticfiles/
 │   ├── media/
 └── portal_website/
```

❌ Never deploy from `/root`

---

## 3️⃣ Virtual Environment + Dependencies

```bash
cd ~/apps/main_website
python3 -m venv venv
source venv/bin/activate
pip install django gunicorn psycopg2-binary
deactivate
```

Repeat per app.

---

## 4️⃣ PostgreSQL Setup

```bash
sudo apt install postgresql postgresql-contrib -y
sudo -i -u postgres
psql
```

```sql
CREATE USER django_user WITH PASSWORD 'STRONG_PASSWORD';
CREATE DATABASE main_db OWNER django_user;
CREATE DATABASE portal_db OWNER django_user;
\q
```

---

## 5️⃣ Django Database Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'main_db',
        'USER': 'django_user',
        'PASSWORD': 'STRONG_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```bash
python manage.py migrate
```

---

## 6️⃣ Gunicorn systemd Service (CRITICAL)

### `/etc/systemd/system/main_website.service`

```ini
[Unit]
Description=Main Website Gunicorn
After=network.target

[Service]
User=maishaapp
Group=www-data
WorkingDirectory=/home/maishaapp/apps/main_website
ExecStart=/home/maishaapp/apps/main_website/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/maishaapp/apps/main_website/main_website.sock \
          projectname.wsgi:application
UMask=007

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start main_website
sudo systemctl enable main_website
```

✅ **Gunicorn must point to venv**

---

## 7️⃣ Nginx Configuration

### `/etc/nginx/sites-available/main_website`

```nginx
server {
    server_name maishaapp.co.tz www.maishaapp.co.tz;

    location /static/ {
        alias /home/maishaapp/apps/main_website/staticfiles/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /home/maishaapp/apps/main_website/media/;
    }

    location / {
        proxy_pass http://unix:/home/maishaapp/apps/main_website/main_website.sock;
        include proxy_params;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/main_website /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 8️⃣ Permissions (THIS FIXES 502s)

Nginx **must traverse directories**:

```bash
sudo chmod o+x /home/maishaapp
sudo chmod o+x /home/maishaapp/apps
sudo chmod o+x /home/maishaapp/apps/main_website
```

Test:

```bash
sudo -u www-data ls /home/maishaapp/apps/main_website/
```

---

## 9️⃣ Static Files (No More 404s)

```bash
python manage.py collectstatic
```

Gunicorn **never serves static** — only Nginx does.

---

## 🔐 SSL (Certbot)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx
```

---

## 👑 Django Superuser

```bash
source venv/bin/activate
python manage.py createsuperuser
deactivate
```

Admin:

```
https://yourdomain.com/admin/
```

---

## 🧪 Debugging Cheatsheet

### 502 Bad Gateway

* Socket path wrong ❌
* Parent directory permissions ❌
* Gunicorn not running ❌

```bash
sudo systemctl status main_website
ls -l main_website.sock
sudo tail -f /var/log/nginx/error.log
```

### Gunicorn fails

* Wrong `wsgi` module
* Wrong user
* Wrong venv path

---

## ✅ Production Rules (Burn These In)

* ❌ Never run Django with `runserver`
* ❌ Never deploy from `/root`
* ✅ One venv per app
* ✅ One systemd service per app
* ✅ Nginx serves static/media
* ✅ PostgreSQL user ≠ postgres

---

## 🏁 Final Notes

If you follow this README **exactly**, deployment becomes boring.
And boring deployments = money + sanity.

You earned this file the hard way 😄
