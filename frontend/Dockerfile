# syntax=docker/dockerfile:1

##############################################################################
# Builder stage
#
# Installs ALL dependencies (including devDependencies) and compiles the app.
# Vite and @vitejs/plugin-react are devDependencies but are REQUIRED at build
# time — `npm ci --only=production` here was the original build failure.
##############################################################################
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (this layer is cached until the lockfile changes).
COPY package.json package-lock.json ./
RUN npm ci

# Compile the production bundle into /app/dist.
COPY . .
RUN npm run build

##############################################################################
# Final stage
#
# Production-only: static assets + a minimal, NON-ROOT nginx
# (nginx-unprivileged runs as uid 101, listens on 8080). No node_modules,
# no npm, no build tooling — nothing from the builder except /app/dist.
##############################################################################
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
