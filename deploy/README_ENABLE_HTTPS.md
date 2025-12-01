LostLink Kenya — Enable HTTPS on Ubuntu 22.04 (Let's Encrypt)

This README contains step-by-step commands and configuration templates. Replace placeholders before running.

Prereqs (on VPS)
- A domain: www.lostlinkkenya.com (you own it and can edit DNS)
- VPS with public IP and Ubuntu 22.04
- SSH access and sudo
- Project code placed at /home/ubuntu/myproject (adjust paths below)

High-level steps
1. Create DNS A record -> point lostlinkkenya.com and www.lostlinkkenya.com to your VPS public IP.
2. SSH into the VPS and run commands below to install packages, create venv, run migrations, collectstatic, configure gunicorn and nginx.
3. Use certbot to obtain and install Let's Encrypt certificate.
4. Update Django settings for production and HTTPS.

Exact commands (run as sudo or ubuntu user with sudo)

# --- SYSTEM PREP ---
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git ufw

# --- CREATE PROJECT USER / CLONE (optional) ---
# If you already have project files on the server, skip clone and adapt paths
cd /home/ubuntu
git clone <your-repo-url> myproject
cd myproject

# Create virtualenv and install
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Django setup
# Make sure your DATABASES configuration is correct and accessible
python manage.py migrate
python manage.py collectstatic --noinput

# Create systemd unit for gunicorn (copy the provided template)
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
# Edit file if your USER / WorkingDirectory / PATH differ
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo systemctl status gunicorn

# Configure nginx
# Copy the provided nginx config and enable it
sudo cp deploy/nginx_lostlinkkenya.conf /etc/nginx/sites-available/lostlinkkenya
# Edit aliases in the file to match your STATIC_ROOT and MEDIA_ROOT
sudo ln -s /etc/nginx/sites-available/lostlinkkenya /etc/nginx/sites-enabled/
# Remove default if you want
sudo rm /etc/nginx/sites-enabled/default || true
sudo nginx -t
sudo systemctl restart nginx

# Open firewall ports
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status

# --- Let's Encrypt certificate using certbot ---
sudo apt install -y certbot python3-certbot-nginx
# This will request and automatically configure nginx to use the cert
sudo certbot --nginx -d lostlinkkenya.com -d www.lostlinkkenya.com

# Certbot will prompt for contact email and agree to TOS, then obtain cert and reload nginx.
# Confirm renewal timer
sudo systemctl status certbot.timer
# Test renewal (dry-run)
sudo certbot renew --dry-run

# --- Django production settings (important) ---
# Edit myproject/settings.py and apply the changes below, or add them to environment-managed config
# Example production snippet:

# myproject/settings.py (production additions)
ALLOWED_HOSTS = ['lostlinkkenya.com', 'www.lostlinkkenya.com']
DEBUG = False

# When served behind nginx/Proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = ['https://lostlinkkenya.com', 'https://www.lostlinkkenya.com']

# Optional security hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True  # ensures all traffic uses HTTPS

# Ensure STATIC_ROOT and MEDIA_ROOT are set and collectstatic has been run
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# After editing settings, restart gunicorn
sudo systemctl restart gunicorn

# --- Verify ---
# Open https://lostlinkkenya.com in your browser. Use logs to debug if problems occur:
# nginx errors: /var/log/nginx/lostlinkkenya.error.log
# gunicorn logs: sudo journalctl -u gunicorn -b

Notes and troubleshooting
- If certbot fails with a challenge error, verify DNS A records are correct and the domain points to the server IP. Also ensure port 80 is open and not blocked by provider firewalls.
- If you use Cloud provider load balancer, you may need to add additional steps for TLS termination.
- For automatic deploys, consider using supervisor or systemd and a deploy script.

Security reminder
- Don't set DEBUG=True in production
- Use strong passwords and limit SSH access (use SSH keys)

If you want, I can:
- Generate the exact nginx config and systemd unit files already (done in deploy/)
- Patch `myproject/settings.py` here (I can create a safe patch file showing the insertion) — tell me if you want me to prepare that file.
- Walk you through the commands on your VPS live if you paste the server output here.

