from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add the parent directory to sys.path to allow imports from your project's modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app  # Import the Flask app where app is defined
from database import Base  # Import the Base from your database module

# Alembic configuration
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the sqlalchemy.url config to your Flask app's SQLALCHEMY_DATABASE_URI
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

# The metadata object is needed for Alembic's autogenerate feature
target_metadata = Base.metadata

# Other Alembic configuration
# ...

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode. This configures the context with an Engine,
    and associate a connection with the context.
    """
    # This line overrides the ini-file sqlalchemy.url with the one from your Flask app
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = app.config['SQLALCHEMY_DATABASE_URI']
    
    connectable = engine_from_config(
        configuration=configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# Determine whether to run in offline or online mode
if context.is_offline_mode():
    run_migrations_offline() 
else:
    run_migrations_online()
