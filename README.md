# Pleth: Ethereum Library For Humans

Pleth is a project that aims to provide human-friendly interfaces for common ethereum operations. Pleth is written in pure python and almost zero dependencies except the standard library.

## Installation

```sh
$ pip install pleth
# or
$ git clone https://github.com/libraries/pleth
$ cd pleth
$ python -m pip install --editable .
```

## Usage

By default, pleth is configured on the develop. To switch networks, use `pleth.config.current = pleth.config.mainnet`.

**example/addr.py**

Calculate the address from a private key.

```sh
$ python example/addr.py --prikey 0x1

# 0x7e5f4552091a69125d5dfcb7b8c2659029395bdf
```

**example/balance.py**

Get the balance by an address.

```sh
$ python example/balance.py --addr 0x7e5f4552091a69125d5dfcb7b8c2659029395bdf

# 39934.9989371221
```

**example/collision.py**

Generate a random private key and check whether there are assets under the private key.

```sh
$ python example/collision.py --net mainnet
```

**example/scan_erc20.py**

Print all usdt transfer events in the last block.

```sh
$ python example/scan_erc20.py

# 0x4d74d6fb5a75d121cda9f9dfbd0bd074999b43731f17140606ea57eccb5a7192
# 0x11b815efb8f581194ae79006d24e0d814b7697f6 0xa69babef1ca67a37ffaf7a485dfff3382056e78c 135241.983213
# ...
```

**example/scan_eth.py**

Get the latest block and print out the transaction hash, sender, receiver and value(in ether).

```sh
$ python example/scan_eth.py --net mainnet

# 0x41733e4e2b1537c9be99ad591c2e2a608dbff547ebd91acbb65e9a205aceb3ff
# 0x9ab23085cb3e847d37819a712512dfd5d60c8d88 0x429cf888dae41d589d57f6dc685707bec755fe63 1.9937829e-11
# ...
```

**example/storage.py**

Publish a storage contract, then store a number 42 in the contract, and finally read this number.

```sh
$ python example/storage.py --action deploy --prikey 0x1
# hash = 0xc4a663c8a867d1d6fcbb8b57794eb732baa1bf6cb4c1b0c1cee278e00c8fd644
# addr = 0x930b793f778bbf43fab1080abf1840e018831cde

$ python example/storage.py --action set --addr 0x930b793f778bbf43fab1080abf1840e018831cde --prikey 0x1
# hash = 0x95c3fab08f6f4dcac14db157c2c2936417ae528acf9637fd50f772ac617072b5

$ python example/storage.py --action get --addr 0x930b793f778bbf43fab1080abf1840e018831cde
# data = 0x000000000000000000000000000000000000000000000000000000000000002a
```

**example/transfer.py**

Transfer ether to other.

```sh
$ python example/transfer.py --prikey 0x1 --to 0x2b5ad5c4795c026514f8317c7a215e218dccd6cf --value 0.05
# 0xfdeb27f32a21c793562daa8fa2780546e3304620a9925337c7df5e4e9819ef3a
```

**example/erc20_balance.py**

Get erc20 token balance by holder address.

```sh
$ python example/erc20_balance.py --net mainnet --token usdt --addr 0xF977814e90dA44bFA03b6295A0616a897441aceC
# 19967378226.983707
```

**example/erc20_transfer.py**

Transfer erc20 token to other.

```sh
$ python example/erc20_transfer.py --prikey 0x1 --token usdt --to 0x2b5ad5c4795c026514f8317c7a215e218dccd6cf --value 1.25
# 0x...
```

## Test

```sh
$ git clone https://github.com/ethereum/go-ethereum --branch release/1.17
$ cd go-ethereum
$ make geth

$ geth --dev --http
$ geth --exec "eth.sendTransaction({from: eth.accounts[0], to: '0x7e5f4552091a69125d5dfcb7b8c2659029395bdf', value: web3.toWei(10000, 'ether')})" attach /tmp/geth.ipc
$ pytest -v
```

## License

MIT
