import json
import pleth.abi
import pleth.config
import pleth.core
import pleth.denomination
import pleth.rpc
import typing


class WalletTransactionAnalyzer:
    def __init__(self, tx: pleth.core.TxLegacy) -> None:
        self.tx = tx

    def analyze_gas_price(self) -> None:
        # Make sure the gas price is less than 32 gwei. This is a simple check, but it works well in most cases.
        assert self.tx.gas_price < 32 * pleth.denomination.gwei

    def analyze(self) -> None:
        self.analyze_gas_price()


class Wallet:
    def __init__(self, prikey: int) -> None:
        self.prikey = pleth.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = self.pubkey.addr()

    def __eq__(self, other) -> bool:
        return all([
            self.prikey == other.prikey,
            self.pubkey == other.pubkey,
            self.addr == other.addr,
        ])

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr.hex(),
        }

    def balance(self) -> int:
        return int(pleth.rpc.eth_get_balance(f'0x{self.addr.hex()}', 'latest'), 0)

    def contract_addr(self, hash: bytearray) -> bytearray:
        return bytearray.fromhex(pleth.rpc.eth_get_transaction_receipt(f'0x{hash.hex()}')['contractAddress'][2:])

    def contract_call(self, addr: bytearray, data: bytearray) -> bytearray:
        return bytearray.fromhex(pleth.rpc.eth_call({
            'from': f'0x{self.addr.hex()}',
            'to': f'0x{addr.hex()}',
            'input': f'0x{data.hex()}',
        }, 'latest')[2:])

    def contract_deploy(self, data: bytearray) -> bytearray:
        gas_price = int(pleth.rpc.eth_gas_price(), 0)
        gas = pleth.config.current.gas_base_fee * 100
        value = 0
        tx = pleth.core.TxLegacy(self.nonce(), gas_price, gas, None, value, data)
        return self.send(tx)

    def contract_exec(self, addr: bytearray, value: int, data: bytearray) -> bytearray:
        gas_price = int(pleth.rpc.eth_gas_price(), 0)
        gas = pleth.config.current.gas_base_fee * 100
        tx = pleth.core.TxLegacy(self.nonce(), gas_price, gas, addr, value, data)
        return self.send(tx)

    def erc20_balance(self, addr: bytearray) -> int:
        func = pleth.abi.function_selector('balanceOf', ['address'])
        args = pleth.abi.argument_encoding([pleth.abi.Address], [self.addr])
        data = func + args
        rets = self.contract_call(addr, data)
        rets = pleth.abi.argument_decoding([pleth.abi.Uint256], rets)
        return rets[0]

    def erc20_decimals(self, addr: bytearray) -> int:
        data = pleth.abi.function_selector('decimals', [])
        rets = self.contract_call(addr, data)
        rets = pleth.abi.argument_decoding([pleth.abi.Uint8], rets)
        return rets[0]

    def erc20_transfer(self, addr: bytearray, to: bytearray, value: int) -> bytearray:
        func = pleth.abi.function_selector('transfer', ['address', 'uint256'])
        args = pleth.abi.argument_encoding([pleth.abi.Address, pleth.abi.Uint256], [to, value])
        return self.contract_exec(addr, 0, func + args)

    def erc20_transfer_all(self, addr: bytearray, to: bytearray) -> bytearray:
        return self.erc20_transfer(addr, to, self.erc20_balance(addr))

    def erc20_transfer_from(self, addr: bytearray, spender: bytearray, to: bytearray, value: int) -> bytearray:
        func = pleth.abi.function_selector('transferFrom', ['address', 'address', 'uint256'])
        args = pleth.abi.argument_encoding(
            [pleth.abi.Address, pleth.abi.Address, pleth.abi.Uint256],
            [spender, to, value],
        )
        hash = self.contract_exec(addr, 0, func + args)
        return hash

    def erc20_approve(self, addr: bytearray, spender: bytearray, value: int) -> bytearray:
        func = pleth.abi.function_selector('approve', ['address', 'uint256'])
        args = pleth.abi.argument_encoding([pleth.abi.Address, pleth.abi.Uint256], [spender, value])
        hash = self.contract_exec(addr, 0, func + args)
        return hash

    def erc20_allowance(self, addr: bytearray, owner: bytearray, spender: bytearray) -> int:
        func = pleth.abi.function_selector('allowance', ['address', 'address'])
        args = pleth.abi.argument_encoding([pleth.abi.Address, pleth.abi.Address], [owner, spender])
        rets = self.contract_call(addr, func + args)
        rets = pleth.abi.argument_decoding([pleth.abi.Uint256], rets)
        return rets[0]

    def nonce(self) -> int:
        return int(pleth.rpc.eth_get_transaction_count(f'0x{self.addr.hex()}', 'pending'), 0)

    def send(self, tx: pleth.core.TxLegacy) -> bytearray:
        tx.sign(self.prikey)
        WalletTransactionAnalyzer(tx).analyze()
        hash = pleth.rpc.eth_send_raw_transaction(f'0x{tx.envelope().hex()}')
        assert tx.hash() == bytearray.fromhex(hash[2:])
        return tx.hash()

    def transfer(self, addr: bytearray, value: int) -> bytearray:
        gas_price = int(pleth.rpc.eth_gas_price(), 0)
        gas = pleth.config.current.gas_base_fee
        tx = pleth.core.TxLegacy(self.nonce(), gas_price, gas, addr, value, bytearray())
        return self.send(tx)

    def transfer_all(self, addr: bytearray) -> bytearray:
        gas_price = int(pleth.rpc.eth_gas_price(), 0)
        gas = pleth.config.current.gas_base_fee
        value = self.balance() - gas * gas_price
        tx = pleth.core.TxLegacy(self.nonce(), gas_price, gas, addr, value, bytearray())
        return self.send(tx)

    @classmethod
    def view_only(cls, addr: bytearray) -> typing.Self:
        # View only wallet let you monitor a wallet's balance and activity but you can't send, swap, or sign
        # transactions.
        wallet = cls(0)
        wallet.addr = addr
        return wallet
