from db import db

try:
        db.delete_table(TableName='Reader')
except Exception as e:
    print("Error deleting table:", e)