import ijson
import pprint
import argparse
import json
import psycopg2

conn = psycopg2.connect(dbname='postgres', user='postgres', 
                        password='gozogozogoz', host='localhost')
conn.autocommit = True
cursor = conn.cursor()

parser = argparse.ArgumentParser()
parser.add_argument("json_path", nargs='?', default="events.json")
args = parser.parse_args()



        
different_structures = []
first_occurence = {}

f = open(args.json_path)
msgs = ijson.items(f, '', multiple_values = True)
i = 0
try: 
    for msg in msgs:
        my_json = json.dumps(msg)
        sql = "INSERT INTO json_test (data) VALUES (%s)"
        #print(cursor.execute(sql, (my_json,)))
        #print (cursor.fetchone()[0])
        i = i+1
except Exception as e:
    print(e)
conn.commit()
print(i)