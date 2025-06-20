FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy the rest of the code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the built application with a lightweight web server
FROM nginx:alpine

# Copy the built app to nginx's serve directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port that nginx will run on
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
