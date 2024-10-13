FROM nginx:latest

RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/* 

COPY /staticfiles /usr/share/nginx/html/staticfiles/
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY renew_certificates.sh /usr/local/bin/renew_certificates.sh
RUN chmod +x /usr/local/bin/renew_certificates.sh


CMD ["nginx", "-g", "daemon off;"]
