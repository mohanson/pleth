import pleth
import secrets


def test_sign():
    prikey = pleth.secp256k1.Fr(max(1, secrets.randbelow(pleth.secp256k1.N)))
    pubkey = pleth.secp256k1.G * prikey
    m = pleth.secp256k1.Fr(max(1, secrets.randbelow(pleth.secp256k1.N)))
    r, s, v = pleth.ecdsa.sign(prikey, m)
    assert pleth.ecdsa.verify(pubkey, m, r, s)
    assert pleth.ecdsa.pubkey(m, r, s, v) == pubkey


def test_verify():
    prikey = pleth.secp256k1.Fr(1)
    pubkey = pleth.secp256k1.G * prikey
    assert pubkey.x == pleth.secp256k1.Fq(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)
    assert pubkey.y == pleth.secp256k1.Fq(0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
    m = pleth.secp256k1.Fr(0xdec0535dee8e3667e1ea05c7614b5c16a7a76c7eb22464d8e2a64b4db4f97457)
    r = pleth.secp256k1.Fr(0x4ad35a57975598ca16b32feaa404baff0ebec69409ac14182fdab9060cd5f7ef)
    s = pleth.secp256k1.Fr(0x7f486b1aeebf383de2957cb0db1b48f87c7c42420f3298b25e1466ea6892d02e)
    assert pleth.ecdsa.verify(pubkey, m, r, s)


def test_pubkey():
    prikey = pleth.secp256k1.Fr(1)
    pubkey = pleth.secp256k1.G * prikey
    assert pubkey.x == pleth.secp256k1.Fq(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)
    assert pubkey.y == pleth.secp256k1.Fq(0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
    m = pleth.secp256k1.Fr(0xdec0535dee8e3667e1ea05c7614b5c16a7a76c7eb22464d8e2a64b4db4f97457)
    r = pleth.secp256k1.Fr(0x4ad35a57975598ca16b32feaa404baff0ebec69409ac14182fdab9060cd5f7ef)
    s = pleth.secp256k1.Fr(0x7f486b1aeebf383de2957cb0db1b48f87c7c42420f3298b25e1466ea6892d02e)
    v = 0
    assert pleth.ecdsa.pubkey(m, r, s, v) == pubkey
