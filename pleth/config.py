import pleth.objectdict
import random
import requests


develop = pleth.objectdict.ObjectDict({
    'chain_id': 1337,
    'erc20': {},
    'gas_base_fee': 21000,
    'rpc': {
        'url': 'http://127.0.0.1:8545',
        'qps': 32,
    }
})

mainnet = pleth.objectdict.ObjectDict({
    'chain_id': 1,
    'erc20': {
        'usdc': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'usdt': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    },
    'gas_base_fee': 21000,
    'rpc': {
        'url': 'https://eth.drpc.org',
        'qps': 2,
    }
})

testnet = pleth.objectdict.ObjectDict({
    'chain_id': 11155111,
    'erc20': {},
    'gas_base_fee': 21000,
    'rpc': {
        'url': 'https://rpc.sepolia.org',
        'qps': 2,
    }
})


def upgrade(url: str):
    develop.chain_id = int(requests.post(url, json={
        'id': random.randint(0x00000000, 0xffffffff),
        'jsonrpc': '2.0',
        'method': 'eth_chainId',
        'params': []
    }).json()['result'], 0)
    develop.url = url


current = develop
