from peewee_migrate import Router

from src.models import database


router = Router(database, ignore=['basemodel'])

# Create migration
router.create('migration_name', auto='src.models')

# # Run migration/migrations
# router.run('migration_name')

# Run all unapplied migrations
router.run()
