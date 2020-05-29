import ijson
import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("json_path", nargs='?', default="events.json")
args = parser.parse_args()


def traverse(obj, index, parent):
    if isinstance(obj, dict):
        return {k: traverse(v, k, obj) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [traverse(elem, index, obj) for index, elem in enumerate(obj)]
    else:
        parent[index] = ""

def traverse2(obj, index, parent):
    if isinstance(obj, dict):
        return {k: traverse2(v, k, obj) for k, v in obj.items()}
    elif isinstance(obj, list):
        if len(obj) > 0 and obj[0] == '':
            parent[index] = len(obj)
        else:
            return [traverse2(elem, index, obj) for index, elem in enumerate(obj)]
    else:
        parent[index] = ""
        
different_structures = []
first_occurence = {}

f = open(args.json_path)
msgs = ijson.items(f, '', multiple_values = True)
i = 0
try: 
    for msg in msgs:
        msga = [msg]
        traverse(msg, 0 , msga)
        msga = [msg]
        traverse2(msg, 0 , msga)
        if msg not in different_structures:
            different_structures.append(msg)
            first_occurence[i] = msg
    #    recv_count = 

    #    senders = msg['message.sender']
    #    print(senders)
    #    recv_packet_count = len(msg.get('recv_packet.packet_data', []))
    #    print(recv_packet_count)
    #    print(msg)
        i = i + 1
except:
    pass
#cities = (o for o in objects if o['type'] == 'city')
#for city in cities:
#    do_something_with(city) 

pprint.pprint(first_occurence)