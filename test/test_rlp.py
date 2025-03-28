import pleth


def test_encode():
    assert pleth.rlp.encode(bytearray(b'dog')) == bytearray(b'\x83dog')
    assert pleth.rlp.encode([bytearray(b'cat'), bytearray(b'dog')]) == bytearray(b'\xc8\x83cat\x83dog')
    assert pleth.rlp.encode(bytearray()) == bytearray(b'\x80')
    assert pleth.rlp.encode([]) == bytearray(b'\xc0')
    assert pleth.rlp.encode(bytearray([0x00])) == bytearray(b'\x00')
    assert pleth.rlp.encode(bytearray([0x0f])) == bytearray(b'\x0f')
    assert pleth.rlp.encode(bytearray([0x04, 0x00])) == bytearray(b'\x82\x04\x00')
    assert pleth.rlp.encode([[], [[]], [[], [[]]]]) == bytearray(b'\xc7\xc0\xc1\xc0\xc3\xc0\xc1\xc0')
    assert pleth.rlp.encode(bytearray([0] * 56)) == bytearray([0xb8, 0x38] + [0x00] * 56)


def test_decode():
    assert pleth.rlp.decode(bytearray(b'\x83dog')) == bytearray(b'dog')
    assert pleth.rlp.decode(bytearray(b'\xc8\x83cat\x83dog')) == [bytearray(b'cat'), bytearray(b'dog')]
    assert pleth.rlp.decode(bytearray(b'\x80')) == bytearray()
    assert pleth.rlp.decode(bytearray(b'\xc0')) == []
    assert pleth.rlp.decode(bytearray(b'\x00')) == bytearray([0x00])
    assert pleth.rlp.decode(bytearray(b'\x0f')) == bytearray([0x0f])
    assert pleth.rlp.decode(bytearray(b'\x82\x04\x00')) == bytearray([0x04, 0x00])
    assert pleth.rlp.decode(bytearray(b'\xc7\xc0\xc1\xc0\xc3\xc0\xc1\xc0')) == [[], [[]], [[], [[]]]]
    assert pleth.rlp.decode(bytearray([0xb8, 0x38] + [0x00] * 56)) == bytearray([0] * 56)


def test_bool():
    assert pleth.rlp.encode(pleth.rlp.put_bool(1)) == bytearray([0x01])
    assert pleth.rlp.encode(pleth.rlp.put_bool(0)) == bytearray([0x80])
    assert pleth.rlp.get_bool(pleth.rlp.decode(bytearray([0x01]))) == 1
    assert pleth.rlp.get_bool(pleth.rlp.decode(bytearray([0x80]))) == 0


def test_uint():
    assert pleth.rlp.encode(pleth.rlp.put_uint(852456)) == bytearray([0x83, 0x0d, 0x01, 0xe8])
    assert pleth.rlp.encode(pleth.rlp.put_uint(0)) == bytearray([0x80])
    assert pleth.rlp.encode(pleth.rlp.put_uint(0x10000000000000001)) == bytearray([0x89, 0x01, 0, 0, 0, 0, 0, 0, 0, 0x01])
    assert pleth.rlp.get_uint(pleth.rlp.decode(bytearray([0x83, 0x0d, 0x01, 0xe8]))) == 852456
    assert pleth.rlp.get_uint(pleth.rlp.decode(bytearray([0x80]))) == 0
    assert pleth.rlp.get_uint(pleth.rlp.decode(bytearray([0x89, 0x01, 0, 0, 0, 0, 0, 0, 0, 0x01]))) == 0x10000000000000001
