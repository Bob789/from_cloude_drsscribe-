# Stage 1: Build Flutter Web
FROM debian:bookworm-slim AS build

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
ENV FLUTTER_HOME=/opt/flutter
ENV PATH="$FLUTTER_HOME/bin:$PATH"
RUN git clone --depth 1 --branch stable https://github.com/flutter/flutter.git $FLUTTER_HOME \
    && flutter precache --web \
    && flutter config --enable-web \
    && dart --disable-analytics

WORKDIR /app

# Install dependencies first (cache layer)
COPY pubspec.yaml pubspec.lock* ./
RUN flutter pub get

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
