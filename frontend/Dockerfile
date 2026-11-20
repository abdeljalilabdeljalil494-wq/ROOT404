# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS builder

WORKDIR /app

# Install deps with cache
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts && \
    npm cache clean --force

COPY . .

# Build with security checks
RUN npm run build && \
    # Remove source maps in production for security
    find dist -name "*.map" -delete

FROM nginx:alpine

# Security: Remove default config and unnecessary files
RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/* && \
    # Create nginx user already exists, ensure no shell
    adduser -D -H -s /bin/false nginx 2>/dev/null || true

# Copy built frontend
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self';" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;

    # Authorization codes/state must never enter access logs or outgoing referrers.
    location /oauth/callback/ {
        access_log off;
        add_header Referrer-Policy "no-referrer" always;
        add_header Cache-Control "no-store" always;
        try_files $uri /index.html;
    }

    # Frontend routes - SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API proxy - hardened
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer limits to prevent DoS
        client_max_body_size 10m;
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 16k;

        # No caching for API
        add_header Cache-Control "no-store, no-cache, must-revalidate" always;
    }

    # Block hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Block sensitive files
    location ~* \.(env|git|htaccess|htpasswd)$ {
        deny all;
        access_log off;
        log_not_found off;
    }

    location = /ready {
        proxy_pass http://backend:8000/ready;
        access_log off;
        add_header Cache-Control "no-store" always;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "ok\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Security: Set correct permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    # Remove write permissions for group and others
    chmod -R go-w /usr/share/nginx/html && \
    # Secure nginx config
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chmod 644 /etc/nginx/conf.d/default.conf

# Security: Run as nginx user
USER nginx

EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
