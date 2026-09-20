# Stage 1: build static files. Vite bakes VITE_* variables in at build time,
# so the token must be passed as a build argument, not a runtime env.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Declared right before use so a token change does not invalidate the npm ci layer.
ARG VITE_MAPBOX_TOKEN
ARG VITE_API_URL=http://localhost:8000
RUN npm run build

# Stage 2: serve them with nginx.
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
