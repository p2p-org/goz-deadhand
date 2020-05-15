import requests
import logging
import json
from urllib.parse import urljoin
import subprocess
import datetime
import time
import argparse

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("config_path", nargs='?', default="config.json")
args = parser.parse_args()

logging.getLogger().setLevel(logging.INFO)
logging.info("Reading config")
with open(args.config_path) as configfile:
    config = json.load(configfile)

rly = [config['relayer_bin'], '--debug']
if config['relayer_home']:
    rly = rly + ['--home', config['relayer_home']]

def datetime_from_json(json_datetime):
    return datetime.datetime.strptime(json_datetime.split(".")[0], '%Y-%m-%dT%H:%M:%S')

logging.info("getting %s (source) block height and time")
sync_info = requests.get(urljoin(config['source_rpc'], "status")).json()['result']['sync_info']
(src_height, src_time) = (int(sync_info['latest_block_height']), sync_info['latest_block_time'] )
src_time = datetime_from_json(src_time)
logging.info("src_height: %s, src_time: %s"%(src_height, src_time))

logging.info("getting %s (dest) block height and time")
sync_info = requests.get(urljoin(config['destination_rpc'], "status")).json()['result']['sync_info']
(dst_height, dst_time) = (int(sync_info['latest_block_height']), sync_info['latest_block_time'] )
dst_time = datetime_from_json(dst_time)
logging.info("dst_height: %s, dst_time: %s"%(dst_height, dst_time))

time_lag = (src_time - dst_time).total_seconds()
logging.info("Source chain is %d seconds ahead of dest chain" % time_lag)
if time_lag < 5:
    time_lag = 0

def get_client_params(chain, client):
    run_args = rly + [ 'q', 'client', chain, client ]
    logging.info("Running: %s"%(" ".join(run_args)))
    rly_result = subprocess.run(run_args, stdout=subprocess.PIPE).stdout.decode("utf-8")
    logging.info(rly_result)
    client_data = json.loads(rly_result)
    trusting_period = client_data['client_state']['value']['trusting_period']
    last_update = client_data['client_state']['value']['last_header']['signed_header']['header']['time']
    return (trusting_period, last_update)

def update_client(client):
    current_height = src_height
    logging.info("Current src height is %d"%current_height)
    if time_lag > 0:
        current_height = current_height - 1 - \
                         time_lag//config['source_blocktime_seconds']
        current_height = int(current_height)
    logging.info("Checking update header of height %d"%current_height)

    last_height = client['last_height']
    logging.info("There's been a header submitted at height %d"%last_height)

    if(last_height + config['height_lag'] > current_height):
        logging.info("It's less that height lag %d ago, reperating last submitted height" % config['height_lag'])
        current_height = last_height
    else:
        logging.info("It's more that height lag %d ago, submitting new header" % config['height_lag'])
        client['last_height'] = current_height
    
    run_args = rly + [ 'tx', 'raw', "update-client", config['destination_chain_id'], config['source_chain_id'],
                client['client_id'], "--height", str(current_height), "--gas", str(client['gas'])]
    logging.info("Running: %s"%(" ".join(run_args)))
    rly_result = subprocess.run(run_args, stdout=subprocess.PIPE).stdout.decode("utf-8")
    logging.info(rly_result)       


for client in config['clients']:
    logging.info("Working with client %s"%client['client_id'])
    (trusting_period, last_update) = get_client_params(config['destination_chain_id'], client['client_id'])
    logging.info("client: %s, trusting period: %s, last update: %s"% (client['client_id'], trusting_period, last_update))
    
    trusting_period = datetime.timedelta(seconds=int(trusting_period)/1000000000)
    last_update = datetime_from_json(last_update)
    risk_margin = datetime.timedelta(seconds=int(client['risk_margin_seconds']))
    
    expiration = last_update + trusting_period
    #destination chain can lag behind so we comapre to the source chain
    time_left = expiration - src_time
    logging.info("expiration: %s, time left: %s, risk margin: %s"%(expiration, time_left, risk_margin))

    if(time_left<risk_margin):
        logging.info("time to update")
        update_client(client)
    else:
        logging.info("Time left > risk margin, continue")

with open("config.json", "w") as configfile:
    json.dump(config, configfile, indent = 4)

logging.info("--- %s seconds elapsed ---" % (time.time() - start_time))