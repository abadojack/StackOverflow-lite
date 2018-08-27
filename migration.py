from project.config import create_tables


def migration():
    """create db tables"""
    create_tables()


migration()
