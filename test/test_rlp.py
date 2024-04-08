import eth


def test_encode():
    assert eth.rlp.encode(bytearray(b'dog')) == bytearray(b'\x83dog')
    assert eth.rlp.encode([bytearray(b'cat'), bytearray(b'dog')]) == bytearray(b'\xc8\x83cat\x83dog')
    assert eth.rlp.encode(bytearray()) == bytearray(b'\x80')
    assert eth.rlp.encode([]) == bytearray(b'\xc0')
    assert eth.rlp.encode(bytearray([0x00])) == bytearray(b'\x00')
    assert eth.rlp.encode(bytearray([0x0f])) == bytearray(b'\x0f')
    assert eth.rlp.encode(bytearray([0x04, 0x00])) == bytearray(b'\x82\x04\x00')
    assert eth.rlp.encode([[], [[]], [[], [[]]]]) == bytearray(b'\xc7\xc0\xc1\xc0\xc3\xc0\xc1\xc0')
    assert eth.rlp.encode(bytearray([0] * 56)) == bytearray([0xb8, 0x38] + [0x00] * 56)


def test_decode():
    assert eth.rlp.decode(bytearray(b'\x83dog')) == bytearray(b'dog')
    assert eth.rlp.decode(bytearray(b'\xc8\x83cat\x83dog')) == [bytearray(b'cat'), bytearray(b'dog')]
    assert eth.rlp.decode(bytearray(b'\x80')) == bytearray()
    assert eth.rlp.decode(bytearray(b'\xc0')) == []
    assert eth.rlp.decode(bytearray(b'\x00')) == bytearray([0x00])
    assert eth.rlp.decode(bytearray(b'\x0f')) == bytearray([0x0f])
    assert eth.rlp.decode(bytearray(b'\x82\x04\x00')) == bytearray([0x04, 0x00])
    assert eth.rlp.decode(bytearray(b'\xc7\xc0\xc1\xc0\xc3\xc0\xc1\xc0')) == [[], [[]], [[], [[]]]]
    assert eth.rlp.decode(bytearray([0xb8, 0x38] + [0x00] * 56)) == bytearray([0] * 56)
