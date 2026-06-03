import pathlib
import pleth


def test_balance():
    user = pleth.wallet.Wallet(1)
    assert user.balance() != 0


def test_contract_deploy():
    user = pleth.wallet.Wallet(1)
    data = bytearray(pathlib.Path('res/storage').read_bytes())
    hash = user.contract_deploy(data)
    pleth.rpc.wait(f'0x{hash.hex()}')
    addr = user.contract_addr(hash)
    code = pleth.rpc.eth_get_code(f'0x{addr.hex()}', 'latest')
    assert bytearray.fromhex(code[2:]) != bytearray()


def test_transfer():
    user = pleth.wallet.Wallet(1)
    hole = pleth.wallet.Wallet(2)
    a = hole.balance()
    hash = user.transfer(hole.addr, 1 * pleth.denomination.ether)
    pleth.rpc.wait(f'0x{hash.hex()}')
    b = hole.balance()
    assert b == a + 1 * pleth.denomination.ether


def test_transfer_all():
    user = pleth.wallet.Wallet(1)
    hole = pleth.wallet.Wallet(2)
    hash = user.transfer(hole.addr, 1 * pleth.denomination.ether)
    pleth.rpc.wait(f'0x{hash.hex()}')
    hash = hole.transfer_all(user.addr)
    pleth.rpc.wait(f'0x{hash.hex()}')
    assert hole.balance() == 0


def test_erc20_transfer():
    user = pleth.wallet.Wallet(1)
    hole = pleth.wallet.Wallet(2)
    data = bytearray(pathlib.Path('res/erc20').read_bytes())
    hash = user.contract_deploy(data)
    pleth.rpc.wait(f'0x{hash.hex()}')
    addr = user.contract_addr(hash)
    assert user.erc20_balance(addr) == 1000000 * 10 ** 18
    assert hole.erc20_balance(addr) == 0
    hash = user.erc20_transfer(addr, hole.addr, 250000 * 10 ** 18)
    pleth.rpc.wait(f'0x{hash.hex()}')
    assert user.erc20_balance(addr) == 750000 * 10 ** 18
    assert hole.erc20_balance(addr) == 250000 * 10 ** 18
    hash = user.erc20_transfer_all(addr, hole.addr)
    pleth.rpc.wait(f'0x{hash.hex()}')
    assert user.erc20_balance(addr) == 0
    assert hole.erc20_balance(addr) == 1000000 * 10 ** 18


def test_erc20_transfer_from():
    user = pleth.wallet.Wallet(1)
    hole = pleth.wallet.Wallet(2)
    hash = user.transfer(hole.addr, 1 * pleth.denomination.ether)
    pleth.rpc.wait(f'0x{hash.hex()}')
    data = bytearray(pathlib.Path('res/erc20').read_bytes())
    hash = user.contract_deploy(data)
    pleth.rpc.wait(f'0x{hash.hex()}')
    addr = user.contract_addr(hash)
    hash = user.erc20_approve(addr, hole.addr, 500000 * 10 ** 18)
    pleth.rpc.wait(f'0x{hash.hex()}')
    assert user.erc20_allowance(addr, user.addr, hole.addr) == 500000 * 10 ** 18
    hash = hole.erc20_transfer_from(addr, user.addr, hole.addr, 250000 * 10 ** 18)
    pleth.rpc.wait(f'0x{hash.hex()}')
    assert user.erc20_balance(addr) == 750000 * 10 ** 18
    assert hole.erc20_balance(addr) == 250000 * 10 ** 18
    assert user.erc20_allowance(addr, user.addr, hole.addr) == 250000 * 10 ** 18
