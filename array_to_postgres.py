import zipfile
import ijson
import pprint
import argparse
import json
import psycopg2
import os

conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='gozogozogoz', host='localhost')
conn.autocommit = True
cursor = conn.cursor()

parser = argparse.ArgumentParser()
parser.add_argument("json_path", nargs='?', default="events.json")
args = parser.parse_args()



        
different_structures = []
first_occurence = {}
filesize = os.stat(args.json_path).st_size


f=open(args.json_path)

msgs = ijson.items(f, 'item', multiple_values = True)
i = 0
try: 
    for msg in msgs:
        my_json = json.dumps(msg)
        print(msg)
        if(i == 5):
            break
        sql = "INSERT INTO json_test (data) VALUES (%s)"
        #cursor.execute(sql, (my_json,))
        if i%1000 == 0:

            pos = 100*f.tell()/filesize
            print(i, "%.2f"%pos + "%")
        #print (cursor.fetchone()[0])
        i = i+1
except Exception as e:
    print(e)
conn.commit()
print(i)



