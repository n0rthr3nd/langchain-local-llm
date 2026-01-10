# Etapa 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install --legacy-peer-deps

# Copiar el resto del código
COPY . .

# Build de producción
RUN npm run build

# Etapa 2: Nginx para servir archivos estáticos
FROM nginx:alpine

# Copiar archivos compilados desde el builder
# Creamos la estructura de directorios para que coincida con la ruta /ia/chat/
RUN mkdir -p /usr/share/nginx/html/ia/chat
COPY --from=builder /app/dist /usr/share/nginx/html/ia/chat

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
