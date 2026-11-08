#!/usr/bin/env bash
# Connects the booking deposit to Octo (real card payments). Run it in Git Bash on your own computer:   bash deploy/set_octo.sh
# It asks for the keys from your Octo personal account (the secret ones stay hidden while you type) and writes them straight into
# the server's settings: they never appear on screen, in chat or in git. Then it asks Octo for a TEST payment to check the keys.
# To go back to test mode later:   bash deploy/set_octo.sh --off
set -euo pipefail

KEY="${KEY:-$HOME/.ssh/zuhriddin.pem}"
SERVER="${SERVER:-ubuntu@52.65.166.20}"   # the Elastic IP: it stays the same when the server restarts

if [ "${1:-}" = "--off" ]; then
  ssh -i "$KEY" "$SERVER" 'set -e
ENV=/var/www/alitravel/backend/.env
sudo cp "$ENV" /var/www/alitravel/backend/backups/env-before-octo-off-$(date +%Y%m%d-%H%M%S).bak
sudo sed -i -E "/^OCTO_(SHOP_ID|SECRET|UNIQUE_KEY|TEST)=/d" "$ENV"
sudo systemctl restart alitravel
echo "Octo keys removed: deposits are back in test mode (no money moves)."'
  exit 0
fi

echo "Octo personal account -> your shop. You need three things:"
echo "  1) Shop ID (octo_shop_id), a number"
echo "  2) Secret key (octo_secret)"
echo "  3) Unique key for signatures (given by Octo's technical team)"
echo
read -r -p "Shop ID: " SHOP
SHOP="${SHOP//[[:space:]]/}"
if ! [[ "$SHOP" =~ ^[0-9]+$ ]]; then echo "The Shop ID is a number; got '$SHOP'. Nothing was changed."; exit 1; fi
read -r -s -p "Secret key (hidden): " SECRET; echo
read -r -s -p "Unique key (hidden): " UNIQUE; echo
SECRET="${SECRET//[[:space:]]/}"; UNIQUE="${UNIQUE//[[:space:]]/}"
if [ -z "$SECRET" ] || [ -z "$UNIQUE" ]; then echo "Both keys are needed. Nothing was changed."; exit 1; fi
read -r -p "Use Octo's TEST transactions for now (no real money)? [y/N]: " TESTMODE
case "$TESTMODE" in [yY]*) TESTMODE=true ;; *) TESTMODE=false ;; esac

printf '%s\n%s\n%s\n%s\n' "$SHOP" "$SECRET" "$UNIQUE" "$TESTMODE" | ssh -i "$KEY" "$SERVER" 'set -e
read -r SHOP; read -r SECRET; read -r UNIQUE; read -r TESTMODE
ENV=/var/www/alitravel/backend/.env
sudo cp "$ENV" /var/www/alitravel/backend/backups/env-before-octo-$(date +%Y%m%d-%H%M%S).bak
setkey() { if sudo grep -qE "^$1=" "$ENV"; then sudo sed -i "s|^$1=.*|$1=$2|" "$ENV"; else echo "$1=$2" | sudo tee -a "$ENV" >/dev/null; fi; }
setkey OCTO_SHOP_ID "$SHOP"
setkey OCTO_SECRET "$SECRET"
setkey OCTO_UNIQUE_KEY "$UNIQUE"
setkey OCTO_TEST "$TESTMODE"
sudo systemctl restart alitravel
cd /var/www/alitravel/backend
sudo -u www-data /var/www/alitravel/venv/bin/python manage.py shell -c "
import json, secrets, urllib.request
from django.conf import settings
from django.utils import timezone
body = {\"octo_shop_id\": int(settings.OCTO_SHOP_ID), \"octo_secret\": settings.OCTO_SECRET, \"shop_transaction_id\": \"check-\" + secrets.token_hex(4),
        \"auto_capture\": True, \"test\": True, \"init_time\": timezone.localtime().strftime(\"%Y-%m-%d %H:%M:%S\"), \"total_sum\": 13000, \"currency\": \"UZS\",
        \"description\": \"ALI TRAVEL key check (test, no money)\", \"return_url\": settings.SITE_URL, \"notify_url\": settings.SITE_URL + \"/api/deposits/octo/notify/\"}
req = urllib.request.Request(\"https://secure.octo.uz/prepare_payment\", data=json.dumps(body).encode(), headers={\"Content-Type\": \"application/json\"})
try:
    data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
except Exception as error:
    print(\"Could not reach Octo:\", error); raise SystemExit
if data.get(\"error\") in (0, None) and (data.get(\"data\") or data).get(\"octo_pay_url\"):
    print(\"OK: Octo accepted the keys (a TEST payment page was created; no money moved).\")
else:
    print(\"Octo did not accept the keys:\", data.get(\"errMessage\") or data.get(\"errorMessage\") or data)
" 2>&1 | grep -vE "imported|RuntimeWarning" | tail -3
echo "Mode: $( [ "$TESTMODE" = true ] && echo "Octo TEST transactions" || echo "REAL payments" )"'
echo "Done. In the admin panel, Settings -> Booking deposit now says whether Octo is connected."
