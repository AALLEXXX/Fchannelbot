#!/bin/sh

# Initialize the database cluster if not already initialized
if [ ! -s /var/lib/postgresql/data/PG_VERSION ]; then
   initdb -D /var/lib/postgresql/data
fi

# Start the PostgreSQL server
pg_ctl start -D /var/lib/postgresql/data -l /var/lib/postgresql/data/logfile

# Wait for the PostgreSQL server to start
sleep 5

# Create the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOF
CREATE DATABASE furys_db;
EOF

# Configure pg_hba.conf to allow connections from any IP address
PG_HBA_PATH="/var/lib/postgresql/data/pg_hba.conf"
echo "host    all             all             0.0.0.0/0            trust" >> "$PG_HBA_PATH"


# Stop the PostgreSQL server
pg_ctl stop -D /var/lib/postgresql/data

# Restart PostgreSQL with the new configuration
postgres -c config_file=/var/lib/postgresql/data/postgresql.conf
