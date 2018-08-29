from project.database import create_tables


def migration():
    """create db tables"""
    create_tables()


migration()
