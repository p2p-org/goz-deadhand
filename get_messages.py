import ijson
import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("json_path", nargs='?', default="events.json")
parser.add_argument("message_position", nargs='?', default=1)
parser.add_argument("prefetch", nargs='?', default=1)
parser.add_argument("postfetch", nargs='?',default=0)
args = parser.parse_args()



        
different_structures = []
first_occurence = {}

f = open(args.json_path)
msgs = ijson.items(f, '', multiple_values = True)
i = 0
try: 
    for msg in msgs:
        if (i >= args.message_position - args.prefetch) and (i <= args.message_position + args.prefetch):
            print(i)
            pprint.pprint(msg)
        i = i + 1
except:
    pass

pprint.pprint(first_occurence)