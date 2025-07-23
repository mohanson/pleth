import argparse
import pleth
import random

# Generate a random private key and check whplether there are assets under the private key.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--limit', type=int, default=8, help='number of attempts')
args = parser.parse_args()

if args.net == 'develop':
    pleth.config.upgrade('http://127.0.0.1:8545')
    pleth.config.current = pleth.config.develop
if args.net == 'mainnet':
    pleth.config.current = pleth.config.mainnet
if args.net == 'testnet':
    pleth.config.current = pleth.config.testnet

for _ in range(args.limit):
    prikey = pleth.core.PriKey.random()
    pubkey = prikey.pubkey()
    addr = pubkey.addr()
    number = pleth.rpc.eth_get_balance(f'0x{addr.hex()}', 'latest')
    print(prikey.json()['n'], number)
    if number != '0x0':
        break
