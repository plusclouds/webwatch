#!/bin/sh

# Determine the port based on the ENVIRONMENT variable
if [ "$ENVIRONMENT" = "production" ]; then
    export APP_PORT=8000
else
    export APP_PORT=5000
fi

# Substitute the APP_PORT in nginx.conf and start nginx
envsubst '$APP_PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start Nginx
nginx -g 'daemon off;'
