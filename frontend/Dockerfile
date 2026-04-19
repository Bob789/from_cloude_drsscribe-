# Stage 1: Build Flutter Web
# Use pre-built Flutter image to avoid cloning Flutter from GitHub on every build
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Install dependencies first (cache layer)
COPY pubspec.yaml pubspec.lock* ./
RUN flutter pub get --no-example

# Copy source and build
COPY . .

# Add build mode argument
ARG BUILD_MODE=debug
RUN flutter build web --${BUILD_MODE} --no-tree-shake-icons

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
