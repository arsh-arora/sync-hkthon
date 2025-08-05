FROM node:18-alpine

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=development
ENV VITE_HOST=0.0.0.0
ENV VITE_PORT=5173

# Install system dependencies
RUN apk add --no-cache \
    curl \
    git

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs \
    && adduser -S nextjs -u 1001 \
    && chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Run the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
