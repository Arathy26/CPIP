# Frontend Dockerfile for CPIP
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy frontend code
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./

# Build for production
RUN npm run build

# Use nginx to serve
FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]