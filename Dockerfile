# Build stage - includes all build dependencies
FROM node:20.19.0-alpine AS builder

WORKDIR /app

# Set production environment for build
ENV NODE_ENV=production

# Install build dependencies
COPY package.json package-lock.json ./

# Update npm to match local environment for consistent behavior
RUN npm install -g npm@11.8.0

# Dependency installation with fallback mechanism
# 
# This Dockerfile implements a two-step dependency installation strategy:
# 1. PRIMARY: npm ci (clean install) - Uses exact versions from package-lock.json
#    - Ensures 100% reproducible builds across environments
#    - Fails if package.json and package-lock.json are out of sync
#    - Required for consistent production deployments
#
# 2. FALLBACK: npm install - Used when npm ci fails due to lock file sync issues
#    - Updates package-lock.json to match package.json dependencies
#    - Allows deployment to continue when lock files are out of sync
#    - WARNING: Reduces build reproducibility - different environments may get different dependency versions
#    - This is a safety mechanism for emergency deployments, not a recommended regular practice
#
# WHY THIS MATTERS:
# - Synchronized lock files ensure every deployment uses exactly the same dependency versions
# - This prevents "works on my machine" issues and makes debugging predictable
# - The fallback should rarely be triggered in normal CI/CD workflows
#
# BEST PRACTICES:
# - Always run 'npm install' locally when updating dependencies
# - Commit both package.json AND package-lock.json together
# - Use pre-build validation (./deploy.sh) to catch sync issues before Docker build
# - Only rely on the fallback for emergency deployments when immediate fixes are needed
#
RUN echo "=== DEPENDENCY INSTALLATION ===" && \
    echo "Starting npm ci (reproducible install)..." && \
    # Try npm ci first - this will fail if package.json and package-lock.json are out of sync
    # Common failure scenarios:
    # - package.json has new dependencies not in package-lock.json
    # - package.json has dependency version changes not reflected in package-lock.json
    # - package-lock.json has entries for dependencies not in package.json
    if npm ci --ignore-scripts; then \
        echo "✅ SUCCESS: npm ci completed - using reproducible dependencies from lock file"; \
    else \
        # Fallback triggered when npm ci exits with non-zero code
        # This indicates lock file synchronization issues
        echo "⚠️  WARNING: npm ci failed - lock files are out of sync"; \
        echo "🔄 FALLING BACK to npm install to continue build..."; \
        echo "ℹ️  NOTE: This allows deployment but reduces build reproducibility"; \
        echo "🔧 FIX: Run 'npm install' locally and commit updated package-lock.json"; \
        # Fallback to npm install - this will update package-lock.json to match package.json
        # WARNING: This may install different dependency versions than what's in the original lock file
        npm install --ignore-scripts; \
        echo "✅ SUCCESS: npm install completed - build continuing with fallback dependencies"; \
    fi && \
    echo "=== DEPENDENCY INSTALLATION COMPLETED ===" && \
    # Clean npm cache to ensure consistent builds and reduce image size
    npm cache clean --force

# Copy source code and build
COPY . .
RUN npm run build

# Runtime stage - lightweight image with only runtime dependencies
FROM node:20.19.0-alpine AS runner

WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Application environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# OpenAI Configuration (build-time args with runtime env defaults)
ARG OPENAI_API_KEY=""
ARG OPENAI_BASE_URL=""
ARG OPENAI_MODEL=""
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV OPENAI_BASE_URL=$OPENAI_BASE_URL
ENV OPENAI_MODEL=$OPENAI_MODEL

# Procurement Agent Configuration (build-time args with runtime env defaults)
ARG LLM_MAX_TOKENS=""
ARG LLM_CONTEXT_WINDOW=""
ARG EMBEDDING_MODEL=""
ENV LLM_MAX_TOKENS=$LLM_MAX_TOKENS
ENV LLM_CONTEXT_WINDOW=$LLM_CONTEXT_WINDOW
ENV EMBEDDING_MODEL=$EMBEDDING_MODEL

# Logging Configuration (build-time args with runtime env defaults)
ARG LOGFIRE_TOKEN=""
ENV LOGFIRE_TOKEN=$LOGFIRE_TOKEN

# Copy necessary files from builder - only what's needed for runtime
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/server ./.next/server
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the application using Next.js standalone production server
# Hostname is controlled by HOSTNAME environment variable
CMD ["node", "server.js"]
