#!/usr/bin/env bash
# Turns on e-mail on the live server: the site then sends booking confirmations to travellers and new-booking letters to the team.
# Run it in Git Bash on your own computer:   bash deploy/set_gmail.sh
# It asks for the Gmail "app password" without showing it and writes it straight into the server's settings (it never leaves
# your computer for anywhere else), then sends a test letter.
set -euo pipefail

KEY="${KEY:-$HOME/.ssh/zuhriddin.pem}"
SERVER="${SERVER:-ubuntu@52.65.166.20}"   # the Elastic IP: it stays the same when the server restarts
GMAIL="${1:-alitravel004@gmail.com}"

echo "Gmail account: $GMAIL"
read -r -s -p "Paste the 16-letter app password (it stays hidden) and press Enter: " PASS; echo
PASS="${PASS// /}"   # Google shows it in groups of four letters
if [ "${#PASS}" -ne 16 ]; then echo "An app password has exactly 16 letters; got ${#PASS}. Nothing was changed."; exit 1; fi

printf '%s\n%s\n' "$GMAIL" "$PASS" | ssh -i "$KEY" "$SERVER" 'set -e
read -r USER; read -r PASS
ENV=/var/www/alitravel/backend/.env
sudo cp "$ENV" /var/www/alitravel/backend/backups/env-before-gmail-$(date +%Y%m%d-%H%M%S).bak
setkey() { if sudo grep -qE "^$1=" "$ENV"; then sudo sed -i "s|^$1=.*|$1=$2|" "$ENV"; else echo "$1=$2" | sudo tee -a "$ENV" >/dev/null; fi; }
setkey EMAIL_HOST smtp.gmail.com
setkey EMAIL_PORT 587
setkey EMAIL_USE_TLS true
setkey EMAIL_USE_SSL false
setkey EMAIL_HOST_USER "$USER"
setkey EMAIL_HOST_PASSWORD "$PASS"
sudo grep -qE "^NOTIFY_EMAILS=.+" "$ENV" || setkey NOTIFY_EMAILS "$USER"
sudo systemctl restart alitravel alitravel-bot
cd /var/www/alitravel/backend
sudo -u www-data /var/www/alitravel/venv/bin/python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
send_mail(\"ALI TRAVEL: e-mail works\", \"This test letter was sent by alitravel.uz. Booking letters will now arrive.\", None, settings.NOTIFY_EMAILS)
print(\"Test letter sent to:\", \", \".join(settings.NOTIFY_EMAILS))
" 2>&1 | grep -vE "imported|RuntimeWarning" | tail -3'
echo "Done. Look in the inbox of the address above (and in Spam the first time)."
