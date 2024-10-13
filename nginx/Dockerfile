# Gunakan Nginx image sebagai base image
FROM nginx:latest

# Install dependencies dan Certbot
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/* 

# Copy default.conf ke dalam container
COPY /staticfiles /usr/share/nginx/html/staticfiles/
COPY nginx.conf /etc/nginx/nginx.conf

# Copy script untuk memperbarui sertifikat
COPY renew_certificates.sh /usr/local/bin/renew_certificates.sh
RUN chmod +x /usr/local/bin/renew_certificates.sh
RUN mkdir -p /var/www/certbot


# Perintah untuk menjalankan Nginx
CMD ["nginx", "-g", "daemon off;"]
