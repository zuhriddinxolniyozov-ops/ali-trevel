#!/usr/bin/env bash
# Runs ON THE SERVER (as root, through sudo) and is started by deploy/aws_deploy.ps1: installs what ALI TRAVEL needs,
# unpacks the uploaded project, starts the website, the Telegram bot and nginx. Safe to run again for an update.
#
#   sudo bash server_setup.sh <package.tgz> <env-file> <domain or ""> <e-mail or ""> <replace-data 0|1>
set -euo pipefail

PACKAGE="${1:?package}"
ENV_FILE="${2:?env file}"
DOMAIN="${3:-}"
EMAIL="${4:-}"
REPLACE_DATA="${5:-0}"
APP=/var/www/alitravel

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m!! %s\033[0m\n' "$*"; }

# ---------- what kind of Linux is this ----------
if command -v apt-get >/dev/null 2>&1; then FAMILY=deb; elif command -v dnf >/dev/null 2>&1; then FAMILY=rpm; else echo "Only Ubuntu/Debian and Amazon Linux/Fedora are supported."; exit 1; fi

say "1/8 Memory and packages"
if [ "$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)" -lt 1500 ] && [ -z "$(swapon --show --noheadings)" ]; then
  say "Small server: adding 1 GB of swap so installs do not run out of memory"
  fallocate -l 1G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab || warn "could not add swap"
fi

PY=python3
if [ "$FAMILY" = deb ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y -q
  apt-get install -y -q nginx curl ca-certificates sqlite3 software-properties-common
  if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'; then
    say "Python 3.12 is needed: adding the deadsnakes repository"
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -y -q
    apt-get install -y -q python3.12 python3.12-venv python3.12-dev
    PY=python3.12
  else
    apt-get install -y -q python3-venv python3-pip
  fi
  [ -n "$DOMAIN" ] && apt-get install -y -q certbot python3-certbot-nginx || true
else
  dnf install -y -q nginx curl sqlite
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'; then dnf install -y -q python3-pip; else dnf install -y -q python3.12 python3.12-pip; PY=python3.12; fi
  [ -n "$DOMAIN" ] && (dnf install -y -q certbot python3-certbot-nginx || warn "certbot could not be installed: HTTPS must be set up by hand") || true
fi
id www-data >/dev/null 2>&1 || useradd -r -s /sbin/nologin www-data
"$PY" --version

say "2/8 Unpacking the project into $APP"
mkdir -p "$APP" "$APP/backend/backups"
TAR_EXCLUDE=()
if [ -f "$APP/backend/db.sqlite3" ] && [ "$REPLACE_DATA" != 1 ]; then
  TAR_EXCLUDE+=(--exclude=backend/db.sqlite3)   # an update never overwrites the live database
fi
if [ -f "$APP/backend/db.sqlite3" ] && [ "$REPLACE_DATA" = 1 ]; then
  cp "$APP/backend/db.sqlite3" "$APP/backend/backups/db-before-replace-$(date +%Y%m%d-%H%M%S).sqlite3"
fi
tar -xzf "$PACKAGE" -C "$APP" ${TAR_EXCLUDE[@]+"${TAR_EXCLUDE[@]}"}
find "$APP/deploy" -type f -exec sed -i 's/\r$//' {} +   # files made on Windows may carry CR characters
rm -rf "$APP/frontend/dist.old"

say "3/8 Settings (.env)"
KEEP_SECRET=""
[ -f "$APP/backend/.env" ] && KEEP_SECRET="$(grep -E '^SECRET_KEY=.+' "$APP/backend/.env" | head -1 | cut -d= -f2- || true)"
[ -n "$KEEP_SECRET" ] || KEEP_SECRET="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(60))')"
sed "s|^SECRET_KEY=.*|SECRET_KEY=${KEEP_SECRET}|" "$ENV_FILE" > "$APP/backend/.env"
chown root:www-data "$APP/backend/.env"; chmod 640 "$APP/backend/.env"

say "4/8 Python environment"
[ -x "$APP/venv/bin/python" ] || "$PY" -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip
"$APP/venv/bin/pip" install -q -r "$APP/backend/requirements.txt"
mkdir -p "$APP/backend/media"
chown -R www-data:www-data "$APP/backend" "$APP/venv" "$APP/frontend" 2>/dev/null || true
chown root:www-data "$APP/backend/.env"
chmod -R o+rX "$APP/frontend" "$APP/backend/media"   # nginx reads the website files and the photos

manage() { (cd "$APP/backend" && runuser -u www-data -- "$APP/venv/bin/python" manage.py "$@"); }

say "5/8 Database"
manage migrate --noinput
COUNT="$(manage shell -c 'from api.models import Tour; print(Tour.objects.count())' 2>/dev/null | grep -E '^[0-9]+$' | tail -1 || true)"
if [ "${COUNT:-0}" = 0 ]; then
  say "Empty database: loading the tours, places, hotels and texts"
  manage seed
  manage seed --extras
  warn "No admin account yet: run  sudo -u www-data $APP/venv/bin/python $APP/backend/manage.py createsuperuser  (inside $APP/backend)"
fi
manage collectstatic --noinput >/dev/null 2>&1 || true

say "6/8 Services (website and Telegram bot)"
cp "$APP/deploy/alitravel.service" /etc/systemd/system/alitravel.service
cp "$APP/deploy/alitravel-bot.service" /etc/systemd/system/alitravel-bot.service
systemctl daemon-reload
systemctl enable alitravel >/dev/null 2>&1
systemctl restart alitravel
if grep -qE '^TELEGRAM_BOT_TOKEN=.+' "$APP/backend/.env"; then
  systemctl enable alitravel-bot >/dev/null 2>&1
  systemctl restart alitravel-bot
else
  systemctl disable --now alitravel-bot >/dev/null 2>&1 || true
  warn "TELEGRAM_BOT_TOKEN is empty: the bot was not started"
fi

say "7/8 nginx"
SERVER_NAME="${DOMAIN:+$DOMAIN www.$DOMAIN}"; SERVER_NAME="${SERVER_NAME:-_}"
cat > /etc/nginx/conf.d/alitravel.conf <<NGINX
server {
    listen 80 default_server;
    server_name ${SERVER_NAME};
    client_max_body_size 12M;
    root ${APP}/frontend/dist;
    index index.html;

    location /api/          { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$http_host; proxy_set_header X-Real-IP \$remote_addr; proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto \$scheme; }
    location = /sitemap.xml { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$http_host; proxy_set_header X-Forwarded-Proto \$scheme; }
    location = /robots.txt  { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$http_host; proxy_set_header X-Forwarded-Proto \$scheme; }
    location /media/        { alias ${APP}/backend/media/; expires 30d; add_header Cache-Control "public"; }
    location /assets/       { expires 365d; add_header Cache-Control "public, immutable"; }
    location /              { try_files \$uri /index.html; }
}
NGINX
rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf 2>/dev/null || true
nginx -t
systemctl enable nginx >/dev/null 2>&1
systemctl restart nginx
chmod o+x /var/www "$APP" 2>/dev/null || true

say "8/8 HTTPS"
if [ -n "$DOMAIN" ] && command -v certbot >/dev/null 2>&1; then
  CERT_MAIL=(--register-unsafely-without-email)
  [ -n "$EMAIL" ] && CERT_MAIL=(-m "$EMAIL")
  if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --redirect "${CERT_MAIL[@]}"; then
    sed -i 's/^SECURE_SSL_REDIRECT=.*/SECURE_SSL_REDIRECT=true/; s/^SECURE_HSTS_SECONDS=.*/SECURE_HSTS_SECONDS=31536000/' "$APP/backend/.env"
    systemctl restart alitravel
    echo "HTTPS is on for $DOMAIN"
  else
    warn "A certificate could not be issued (is the domain's DNS record pointing at this server's address?). The site works over http for now; run  sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN  once DNS is ready."
  fi
else
  echo "No domain given: the site is served over http at the server's address."
fi

# With https the bot gets its messages through the website (webhook): a copy polling on another computer cannot take it away.
if [ -n "$DOMAIN" ] && [ -d "/etc/letsencrypt/live/$DOMAIN" ] && grep -qE '^TELEGRAM_BOT_TOKEN=.+' "$APP/backend/.env"; then
  sed -i 's|manage.py telegram_bot.*$|manage.py telegram_bot --webhook|' /etc/systemd/system/alitravel-bot.service
  systemctl daemon-reload
  systemctl restart alitravel-bot
  echo "Telegram bot: answered by the website (webhook)"
fi

# Every morning (08:30 Tashkent) the site checks itself and warns the team in Telegram if the https certificate is about to run out
# or the domain no longer points at this server; it stays silent while all is well.
cat > /etc/cron.d/alitravel-watch <<CRON
30 3 * * * www-data cd $APP/backend && $APP/venv/bin/python manage.py watch_site >> /tmp/alitravel-watch.log 2>&1
CRON
chmod 644 /etc/cron.d/alitravel-watch

say "Checking"
sleep 3
curl -fsS -o /dev/null -w "API   : %{http_code}\n" http://127.0.0.1:8000/api/site-content/ -H 'Host: localhost' || warn "the API did not answer: see  journalctl -u alitravel -n 50"
curl -fsS -o /dev/null -w "Site  : %{http_code}\n" http://127.0.0.1/ || warn "nginx did not answer"
systemctl is-active alitravel alitravel-bot nginx || true
rm -f "$PACKAGE" "$ENV_FILE"
echo "Done."
