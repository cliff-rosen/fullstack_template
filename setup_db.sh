# Install MariaDB (using scoop for Windows)
# First install scoop if you haven't:
# Run in PowerShell:
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# irm get.scoop.sh | iex

scoop install mariadb

# Start MariaDB
mysql.server start

# Connect and setup database
mysql -u root <<EOF
CREATE DATABASE cognify;
CREATE USER 'cognify_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cognify.* TO 'cognify_user'@'localhost';
FLUSH PRIVILEGES;
EOF 
