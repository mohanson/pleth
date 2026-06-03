import argparse
import pathlib
import pleth

parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, choices=['deploy', 'set', 'get'])
parser.add_argument('--addr', type=str, help='addr')
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    pleth.config.upgrade('http://127.0.0.1:8545')
    pleth.config.current = pleth.config.develop
if args.net == 'mainnet':
    pleth.config.current = pleth.config.mainnet
if args.net == 'testnet':
    pleth.config.current = pleth.config.testnet

if args.action == 'deploy':
    user = pleth.wallet.Wallet(int(args.prikey, 0))
    data = bytearray(pathlib.Path('res/storage').read_bytes())
    hash = user.contract_deploy(data)
    print(f'hash = 0x{hash.hex()}')
    pleth.rpc.wait(f'0x{hash.hex()}')
    addr = user.contract_addr(hash)
    print(f'addr = 0x{addr.hex()}')

if args.action == 'set':
    user = pleth.wallet.Wallet(int(args.prikey, 0))
    data = pleth.abi.function_selector('set', ['uint256']) + pleth.abi.argument_encoding([pleth.abi.Uint256], [42])
    hash = user.contract_exec(bytearray.fromhex(args.addr[2:]), 0, data)
    print(f'hash = 0x{hash.hex()}')

if args.action == 'get':
    data = pleth.abi.function_selector('get', [])
    r = pleth.rpc.eth_call({
        'to': args.addr,
        'input': f'0x{data.hex()}'
    }, 'latest')
    print(f'data = {r}')
