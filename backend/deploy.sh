#!/bin/bash

# Pull the latest changes from GitHub
git -C /opt/shlaimanFinder pull origin main

# Set the correct permissions
sudo chown -R www-data:www-data /opt/shlaimanFinder/backend
sudo chmod -R 755 /opt/shlaimanFinder/backend

# Restart Gunicorn and Nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment complete!"
