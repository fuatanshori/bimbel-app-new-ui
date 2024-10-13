# Pointing Your Domain to Your IP Address
# Ensure your domain's DNS records point to your server's IP address.

# Install Certbot
sudo apt update && sudo apt upgrade
sudo apt install certbot

# Obtain SSL Certificates
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -d db.yourdomain.com \
  -d www.db.yourdomain.com \
  -d portainer.yourdomain.com \
  -d www.portainer.yourdomain.com \
  -d monitor.yourdomain.com \
  -d www.monitor.yourdomain.com

# Setup the .env File
# Create and configure the `.env` file as follows:
cat <<EOL > .env
===start .env====
SECRET_KEY=''
STATUS_DEBUG=
IS_DOCKER=
CSRF_TRUSTED_ORIGINS=''
ALLOWED_HOSTS=
MERCHANT_ID=
CLIENT_KEY=
SERVER_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
IS_PRODUCTION=
MYSQL_DATABASE=bimbel
MYSQL_ROOT_PASSWORD=mysqladmin
VIRTUAL_HOST_PORTAINER=portainer.yourdomain.com
===end .env====
EOL

# Explanation of Environment Variables
cat <<EOL >> .env

# Explanation of Environment Variables
SECRET_KEY: A random string that should be kept private and secure.
STATUS_DEBUG: A boolean value indicating debug status (true or false).
IS_DOCKER: A boolean value indicating if running in Docker (true or false).
CSRF_TRUSTED_ORIGINS: Fill with your domain, e.g., 'https://*.yourdomain.com'.
ALLOWED_HOSTS: Specify your domains, e.g., 'www.yourdomain.com,yourdomain.com,localhost,*'.
MERCHANT_ID: Merchant ID from Midtrans.
CLIENT_KEY: Client key from Midtrans.
SERVER_KEY: Server key from Midtrans.
EMAIL_HOST_USER: Your email address (e.g., email@gmail.com).
EMAIL_HOST_PASSWORD: Your email password.
IS_PRODUCTION: Set to boolean indicating if Midtrans is in production status.
MYSQL_DATABASE: Name of the MySQL database (e.g., bimbel).
MYSQL_ROOT_PASSWORD: Password for the MySQL root user (e.g., mysqladmin).
VIRTUAL_HOST_PORTAINER: For example, portainer.yourdomain.com.
EOL

# Running the Application
docker-compose up -d

# Accessing the Services
echo "Access your application at: http://yourdomain.com"
echo "Access the database at: http://db.yourdomain.com"
echo "Access the monitoring service at: http://monitor.yourdomain.com"
echo "Access Portainer at: http://portainer.yourdomain.com"
