#!/bin/sh

# Menunggu Nginx berjalan
sleep 5

# Membuat sertifikat SSL untuk domain dan subdomain
certbot certonly --nginx --non-interactive --agree-tos --email your_email@example.com -d www.fuatanshori.com -d fuatanshori.com -d db.fuatanshori.com -d www.db.fuatanshori.com

# Memindahkan sertifikat ke direktori host
cp -r /etc/letsencrypt /var/www/certbot

# Perintah untuk memperbarui sertifikat secara otomatis
echo "0 0 * * * /usr/local/bin/renew_certificates.sh" | crontab -
