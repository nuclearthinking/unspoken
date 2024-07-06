FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/unspoken/package*.json ./

RUN npm install

COPY frontend/unspoken .

RUN npm run build

FROM caddy:2.7.5

COPY Caddyfile /etc/caddy/Caddyfile

COPY --from=builder /app/dist /var/www/app

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
