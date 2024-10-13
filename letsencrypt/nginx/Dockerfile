# Gunakan Nginx image sebagai base image
FROM nginx:latest

# Install dependencies dan Certbot
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/* 

# Copy konfigurasi Nginx ke dalam container
COPY nginx.conf /etc/nginx/nginx.conf

# Buat direktori untuk menyimpan sertifikat
RUN mkdir -p /etc/letsencrypt

# Perintah untuk menjalankan Nginx
CMD ["nginx", "-g", "daemon off;"]
