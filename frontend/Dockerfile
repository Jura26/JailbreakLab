# Use official Node LTS image
FROM node:20-alpine

WORKDIR /app

# Copy dependency files first (for caching)
COPY package*.json ./

RUN npm install

# Copy the rest of the app
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Default command to start Vite
CMD npm run dev -- --host
