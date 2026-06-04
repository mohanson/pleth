import io
import pleth
import random


def test_function_selector():
    assert pleth.abi.function_selector('transfer', ['address', 'uint256']).hex() == 'a9059cbb'


def test_argument_encoding():
    args_type = [pleth.abi.Address, pleth.abi.Uint256, pleth.abi.Bool, pleth.abi.String]
    args = [
        bytearray.fromhex('7e5f4552091a69125d5dfcb7b8c2659029395bdf'),
        123456789,
        True,
        'Hello, world!',
    ]
    data = pleth.abi.argument_encoding(args_type, args)
    assert pleth.abi.argument_decoding(args_type, data) == args


def test_address():
    k = pleth.abi.Address
    v = bytearray.fromhex('00112233445566778899aabbccddeeff00112233')
    b = k.encode(v)
    assert len(b) == 32
    assert k.decode(io.BytesIO(b)) == v


def test_array():
    k = pleth.abi.Array(pleth.abi.Uint16, 4)
    v = [1, 2, 3, 65535]
    b = k.encode(v)
    assert len(b) == 32 * 4
    assert k.decode(io.BytesIO(b)) == v


def test_bool():
    k = pleth.abi.Bool
    assert k.decode(io.BytesIO(k.encode(True))) is True
    assert k.decode(io.BytesIO(k.encode(False))) is False


def test_bytes():
    k = pleth.abi.Bytes
    v = bytearray(b'pleth-bytes')
    b = k.encode(v)
    assert k.decode(io.BytesIO(b)) == v


def test_function():
    k = pleth.abi.Function
    v = bytearray.fromhex('00112233445566778899aabbccddeeff00112233deadbeef')
    b = k.encode(v)
    assert len(b) == 32
    assert k.decode(io.BytesIO(b)) == v


def test_int():
    k = pleth.abi.Int256
    for _ in range(32):
        v = random.randint(0, (1 << 255) - 1)
        assert k.decode(io.BytesIO(k.encode(v))) == v


def test_slice():
    k = pleth.abi.Slice(pleth.abi.Uint8)
    v = [1, 2, 3, 255]
    b = k.encode(v)
    assert k.decode(io.BytesIO(b)) == v


def test_tuple():
    k = pleth.abi.Tuple([
        pleth.abi.Uint256,
        pleth.abi.Tuple([pleth.abi.Uint256, pleth.abi.Uint256]),
        pleth.abi.String,
        pleth.abi.String,
    ])
    v = [0x123, [0x456, 0x789], '1234567890', 'Hello, world!']
    assert k.decode(io.BytesIO(bytes(k.encode(v)))) == v

    k = pleth.abi.Tuple([pleth.abi.String])
    v = bytearray([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08,
        0x55, 0x53, 0x44, 0x20, 0x43, 0x6f, 0x69, 0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    assert k.decode(io.BytesIO(v))[0] == 'USD Coin'


def test_uint():
    k = pleth.abi.Uint256
    for _ in range(32):
        v = random.randint(0, (1 << 256) - 1)
        assert k.decode(io.BytesIO(k.encode(v))) == v
