import argparse
import pleth

# Transfer erc20 token to other.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--token', type=str, help='erc20 address')
parser.add_argument('--to', type=str, help='to address')
parser.add_argument('--value', type=float, help='token value')
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

user = pleth.wallet.Wallet(int(args.prikey, 0))
to = bytearray.fromhex(args.to[2:])

decimals = user.erc20_decimals(args.token)
decimals_exponent = 10 ** decimals
amount = int(args.value * decimals_exponent)
hash = user.erc20_transfer(args.token, to, amount)
print(f'0x{hash.hex()}')
