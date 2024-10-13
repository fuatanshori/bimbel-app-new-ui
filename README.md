# Pointing Your Domain to Your IP Address
# Make sure your domain's DNS records are configured to point to your server's IP address.

# Install Certbot
sudo apt update && sudo apt upgrade
sudo apt install certbot

# Obtain SSL Certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com -d db.yourdomain.com -d www.db.yourdomain.com -d portainer.yourdomain.com -d www.portainer.yourdomain.com -d monitor.yourdomain.com -d www.monitor.yourdomain.com

# Setup the .env File
# Create and configure the `.env` file as follows:

echo "===start .env====" > .env
echo "SECRET_KEY=''" >> .env
echo "STATUS_DEBUG=" >> .env
echo "IS_DOCKER=" >> .env
echo "CSRF_TRUSTED_ORIGINS=''" >> .env
echo "ALLOWED_HOSTS=" >> .env
echo "MERCHANT_ID=" >> .env
echo "CLIENT_KEY=" >> .env
echo "SERVER_KEY=" >> .env
echo "EMAIL_HOST_USER=" >> .env
echo "EMAIL_HOST_PASSWORD=" >> .env
echo "IS_PRODUCTION=" >> .env
echo "MYSQL_DATABASE=bimbel" >> .env
echo "MYSQL_ROOT_PASSWORD=mysqladmin" >> .env
echo "VIRTUAL_HOST_PORTAINER=portainer.yourdomain.com" >> .env
echo "===end .env====" >> .env

# Explanation of Environment Variables
echo "SECRET_KEY: A random string that should be kept private and secure." >> .env
echo "STATUS_DEBUG: A boolean value indicating debug status (true or false)." >> .env
echo "IS_DOCKER: A boolean value indicating if running in Docker (true or false)." >> .env
echo "CSRF_TRUSTED_ORIGINS: Fill with your domain, e.g., 'https://*.yourdomain.com'." >> .env
echo "ALLOWED_HOSTS: Specify your domains, e.g., 'www.yourdomain.com,yourdomain.com,localhost,*'." >> .env
echo "MERCHANT_ID: Merchant ID from Midtrans." >> .env
echo "CLIENT_KEY: Client key from Midtrans." >> .env
echo "SERVER_KEY: Server key from Midtrans." >> .env
echo "EMAIL_HOST_USER: Your email address (e.g., email@gmail.com)." >> .env
echo "EMAIL_HOST_PASSWORD: Your email password." >> .env
echo "IS_PRODUCTION: Set to boolean indicating if Midtrans is in production status." >> .env
echo "MYSQL_DATABASE: Name of the MySQL database (e.g., bimbel)." >> .env
echo "MYSQL_ROOT_PASSWORD: Password for the MySQL root user (e.g., mysqladmin)." >> .env
echo "VIRTUAL_HOST_PORTAINER: For example, portainer.yourdomain.com." >> .env

# Running the Application
docker-compose up -d

# Accessing the Services
# Access your application at http://yourdomain.com
# Access the database at http://db.yourdomain.com
# Access the monitoring service at http://monitor.yourdomain.com
# Access Portainer at http://portainer.yourdomain.com
