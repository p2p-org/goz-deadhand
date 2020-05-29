import ijson
import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("json_path", nargs='?', default="events.json")
parser.add_argument("height", nargs='?', default=0, type=int)
parser.add_argument("zone", nargs='?', default="gameofzoneshub-2a")
args = parser.parse_args()



        
different_structures = []
first_occurence = {}

f = open(args.json_path)
msgs = ijson.items(f, '', multiple_values = True)
i = 0
#try: 
for msg in msgs:
    if msg["network"] != args.zone:
        if msg['msg'][0]['event_ibc']:
            submsg = next(iter(dict(msg['msg'][0].get('event_ibc')).values()))
            if submsg['data']['tx.height'][0] == str(args.height):
                print(i)
                pprint.pprint(msg)
    i = i + 1
#except:
#    pass
print(i)


