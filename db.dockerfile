# Use the official PostgreSQL image
FROM postgres:15

RUN mkdir -p /home/extensions/

# Copy the initialization script
COPY db.sh /home/extensions/db.sh

# Make the script executable
RUN chmod +x /home/extensions/db.sh

# Switch to the non-root user
USER postgres

# Set the entry point to start the PostgreSQL server
ENTRYPOINT ["sh", "-c", "/home/extensions/db.sh" ]

# Healthcheck to ensure the database is up and running
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
  CMD pg_isready -U $POSTGRES_USER || exit 1
