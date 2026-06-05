import argparse
import pleth

# Get erc20 balance by an address.

parser = argparse.ArgumentParser()
parser.add_argument('--addr', type=str, help='holder address')
parser.add_argument('--token', type=str, help='erc20 address')
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
args = parser.parse_args()

if args.net == 'develop':
    pleth.config.upgrade('http://127.0.0.1:8545')
    pleth.config.current = pleth.config.develop
if args.net == 'mainnet':
    pleth.config.current = pleth.config.mainnet
if args.net == 'testnet':
    pleth.config.current = pleth.config.testnet

if args.token in pleth.config.current.erc20:
    args.token = pleth.config.current.erc20[args.token]
args.token = bytearray.fromhex(args.token[2:])

wallet = pleth.wallet.Wallet.view_only(bytearray.fromhex(args.addr[2:]))
decimals = wallet.erc20_decimals(args.token)
decimals_exponent = 10 ** decimals
balance = wallet.erc20_balance(args.token) / decimals_exponent
print(balance)
