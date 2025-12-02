import db

try:
    db.db.create_table(
        TableName='Temperature',
        KeySchema=[
            {
                'AttributeName': 'index',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'index',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    db.db.create_table(
        TableName='Humidity',
        KeySchema=[
            {
                'AttributeName': 'index',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'index',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    while True:
        temp_status = db.db.describe_table(TableName='Temperature')['Table']['TableStatus']
        hum_status = db.db.describe_table(TableName='Humidity')['Table']['TableStatus']
        if temp_status == 'ACTIVE' and hum_status == 'ACTIVE':
            print("Tables created and active.")
            break

except Exception as e:
    print("Error creating tables:", e)
