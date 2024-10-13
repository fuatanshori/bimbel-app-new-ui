# Use Nginx image as base image
FROM nginx:latest

# Install dependencies and Certbot
RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy static files and Nginx configuration
COPY ./staticfiles /usr/share/nginx/html/staticfiles/
COPY ./nginx.conf /etc/nginx/nginx.conf

# Create necessary directories
RUN mkdir -p /var/www/certbot

# Copy script for certificate renewal
COPY ./renew_certificates.sh /usr/local/bin/renew_certificates.sh
RUN chmod +x /usr/local/bin/renew_certificates.sh

# Command to run Nginx
CMD ["nginx", "-g", "daemon off;"]