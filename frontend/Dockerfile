# Stage 1: build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build -- --configuration production

# Stage 2: serve with nginx
FROM nginx:stable-alpine
COPY --from=builder /app/dist/tfg-front/browser /usr/share/nginx/html
# Copia configuración nginx si la necesitas
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto (opcional, por defecto nginx usa 80)
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
