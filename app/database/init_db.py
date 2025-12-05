import db

try:
    db.db.create_table(
        TableName='Reader',
        KeySchema=[
            {
                'AttributeName': 'timestamp',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    while True:
        status = db.db.describe_table(TableName='Reader')['Table']['TableStatus']
        if status == 'ACTIVE':
            print("Tables created and active.")
            break

except Exception as e:
    print("Error creating tables:", e)
