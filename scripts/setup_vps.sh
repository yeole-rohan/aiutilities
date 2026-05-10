#!/usr/bin/env bash
# One-time VPS provisioning for aiutilities.site
# Run as root on a fresh Ubuntu 22.04/24.04 VPS.
# Usage: bash scripts/setup_vps.sh
set -euo pipefail

REPO_URL="https://github.com/YOUR_GH_USER/toolutility.git"  # CHANGE THIS
APP_DIR=/var/www/aiutilities
DEPLOY_USER=deploy   # SSH user GitHub Actions will connect as
APP_USER=www-data

echo "==> Installing system packages"
apt-get update -q
apt-get install -y python3.12 python3.12-venv python3-pip nginx git

echo "==> Creating deploy user (for GitHub Actions SSH)"
id -u $DEPLOY_USER &>/dev/null || useradd -m -s /bin/bash $DEPLOY_USER
# Add deploy user's public key:
#   mkdir -p /home/deploy/.ssh
#   echo "ssh-ed25519 AAAA..." >> /home/deploy/.ssh/authorized_keys
#   chmod 700 /home/deploy/.ssh && chmod 600 /home/deploy/.ssh/authorized_keys

echo "==> Granting deploy user passwordless restart of aiutilities"
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart aiutilities" \
    > /etc/sudoers.d/deploy-aiutilities
chmod 440 /etc/sudoers.d/deploy-aiutilities

echo "==> Cloning repo to $APP_DIR"
mkdir -p $APP_DIR
git clone $REPO_URL $APP_DIR
chown -R $DEPLOY_USER:$DEPLOY_USER $APP_DIR

echo "==> Creating Python venv"
cd $APP_DIR
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/prod.txt -q

echo ""
echo "==> ACTION REQUIRED: copy your .env file before continuing"
echo "    scp .env root@YOUR_VPS_IP:$APP_DIR/.env"
echo "    Make sure it contains: SECRET_KEY, DATABASE_URL, DJANGO_SETTINGS_MODULE=saas_starter.settings.production"
echo ""
read -rp "Press Enter once .env is in place..."

echo "==> Running migrations and collectstatic"
cd $APP_DIR
source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "==> Installing systemd service"
mkdir -p /var/log/aiutilities
chown $APP_USER:$APP_USER /var/log/aiutilities
cp $APP_DIR/deploy/aiutilities.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable aiutilities
systemctl start aiutilities
systemctl status aiutilities --no-pager

echo "==> Configuring nginx"
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/aiutilities
ln -sf /etc/nginx/sites-available/aiutilities /etc/nginx/sites-enabled/aiutilities
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "Done! Site should be live at http://aiutilities.site"
echo "Next steps:"
echo "  1. Add GitHub secrets: VPS_HOST, VPS_USER=$DEPLOY_USER, VPS_SSH_KEY"
echo "  2. Point aiutilities.site DNS A record to this server's IP"
