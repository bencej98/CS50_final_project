import sqlite3
from flask import Flask
import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

#print(result)

username = "Test"
possession_type = "Cash"
transaction_type = "Withdraw"
amount = -300
connection = sqlite3.connect("test.db")

connection.row_factory = dict_factory

cur = connection.cursor()

'''

cur.execute( """
            INSERT INTO transactions (username, possession_type, transaction_type, amount)
            VALUES (?, ?, ?, ?)
            """
            , (username, possession_type, transaction_type, amount,))


connection.commit()
'''

data = cur.execute("SELECT amount FROM transactions WHERE username = ?", (username,))

data1 = data.fetchall()
sum = 0
for data in data1:
    sum+=data["amount"]

print(sum)

'''
dashboard_data = cur.execute(           """
                                        SELECT possession_type, amount
                                        FROM all_assets
                                        WHERE username = ?
                                        """
                                        , (username,))




dashboard = dashboard_data.fetchall()

credit_amount = 0
data_list = []
 
for data in dashboard:
    if data["possession_type"] == "Cash" :
        cash_amount = data["amount"]
        data_list.append(cash_amount)
    elif data["possession_type"] == "Asset" :
        asset_amount = data["amount"]
    elif data["possession_type"] == "Bank Account" :
        bank_account_amount = data["amount"]
    else:
        credit_amount = data["amount"]
    

print(data_list)

'''








