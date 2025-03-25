import Crypto.Hash.keccak
import itertools
import json
import pleth.config
import pleth.ecdsa
import pleth.rlp
import pleth.secp256k1
import typing


def hash(data: bytearray) -> bytearray:
    k = Crypto.Hash.keccak.new(digest_bits=256)
    k.update(data)
    return bytearray(k.digest())


class PriKey:
    def __init__(self, n: int) -> None:
        self.n = n

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'n': f'{self.n:064x}',
        }

    def pubkey(self):
        pubkey = pleth.secp256k1.G * pleth.secp256k1.Fr(self.n)
        return PubKey(pubkey.x.x, pubkey.y.x)

    def sign(self, data: bytearray) -> bytearray:
        assert len(data) == 32
        m = pleth.secp256k1.Fr(int.from_bytes(data))
        for _ in itertools.repeat(0):
            r, s, v = pleth.ecdsa.sign(pleth.secp256k1.Fr(self.n), m)
            # https://ethereum.github.io/yellowpaper/paper.pdf, Appendix F. Signing Transactions.
            # We declare that an ECDSA signature is invalid unless all the following conditions are true:
            # 1) 0 < r < secp256k1n
            # 2) 0 < s < secp256k1n / 2 + 1
            # 3) v ∈ {0, 1}
            # There is only a small probability that v will get 2 and 3.
            if v > 1:
                continue
            # Here we adjust the sign of s.
            # Doc: https://ethereum.stackexchange.com/questions/55245/why-is-s-in-transaction-signature-limited-to-n-21
            if s.x * 2 >= pleth.secp256k1.N:
                s = -s
                v = 1 - v
            return bytearray(r.x.to_bytes(32)) + bytearray(s.x.to_bytes(32)) + bytearray([v])
        raise Exception


class PubKey:
    def __init__(self, x: int, y: int) -> None:
        # The public key must be on the curve.
        _ = pleth.secp256k1.Pt(pleth.secp256k1.Fq(x), pleth.secp256k1.Fq(y))
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return all([
            self.x == other.x,
            self.y == other.y,
        ])

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def addr(self) -> bytearray:
        b = bytearray()
        b.extend(self.x.to_bytes(32))
        b.extend(self.y.to_bytes(32))
        return hash(b)[12:]

    def json(self) -> typing.Dict:
        return {
            'x': f'{self.x:064x}',
            'y': f'{self.y:064x}'
        }

    def pt(self) -> pleth.secp256k1.Pt:
        return pleth.secp256k1.Pt(pleth.secp256k1.Fq(self.x), pleth.secp256k1.Fq(self.y))

    @classmethod
    def pt_decode(cls, data: pleth.secp256k1.Pt) -> typing.Self:
        return PubKey(data.x.x, data.y.x)


class TxLegacy:
    def __init__(
        self,
        nonce: int,
        gas_price: int,
        gas: int,
        to: typing.Optional[bytearray],
        value: int,
        data: bytearray,
    ) -> None:
        assert isinstance(data, bytearray)
        self.nonce = nonce
        self.gas_price = gas_price
        self.gas = gas
        # None means contract creation.
        self.to = to
        self.value = value
        self.data = data
        # Signature values.
        self.v = 0
        self.r = 0
        self.s = 0

    def __eq__(self, other) -> bool:
        return self.hash() == other.hash()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def envelope(self) -> bytearray:
        return pleth.rlp.encode([
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_price),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            pleth.rlp.put_uint(self.v),
            pleth.rlp.put_uint(self.r),
            pleth.rlp.put_uint(self.s),
        ])

    def hash(self) -> bytearray:
        return hash(self.envelope())

    def json(self) -> typing.Dict:
        return {
            'nonce': self.nonce,
            'gas_price': self.gas_price,
            'gas': self.gas,
            'to': self.to.hex() if self.to else None,
            'value': self.value,
            'data': self.data.hex(),
            'v': self.v,
            'r': self.r,
            's': self.s,
        }

    def sign(self, prikey: PriKey) -> None:
        # EIP-155: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md
        sign = prikey.sign(hash(pleth.rlp.encode([
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_price),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            pleth.rlp.put_uint(pleth.config.current.chain_id),
            pleth.rlp.put_uint(0),
            pleth.rlp.put_uint(0),
        ])))
        self.r = int.from_bytes(sign[0x00:0x20])
        self.s = int.from_bytes(sign[0x20:0x40])
        self.v = sign[0x40] + 35 + pleth.config.current.chain_id * 2


class TxAccessList:
    # TxAccessList is the data of EIP-2930 access list transactions.
    # See https://eips.ethereum.org/EIPS/eip-2930.
    def __init__(
        self,
        nonce: int,
        gas_price: int,
        gas: int,
        to: typing.Optional[bytearray],
        value: int,
        data: bytearray,
    ) -> None:
        assert isinstance(data, bytearray)
        self.chain_id = pleth.config.current.chain_id
        self.nonce = nonce
        self.gas_price = gas_price
        self.gas = gas
        self.to = to
        self.value = value
        self.data = data
        self.access_list = []
        self.v = 0
        self.r = 0
        self.s = 0

    def __eq__(self, other) -> bool:
        return self.hash() == other.hash()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def envelope(self) -> bytearray:
        return bytearray([0x01]) + pleth.rlp.encode([
            pleth.rlp.put_uint(self.chain_id),
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_price),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            self.access_list,
            pleth.rlp.put_uint(self.v),
            pleth.rlp.put_uint(self.r),
            pleth.rlp.put_uint(self.s),
        ])

    def hash(self) -> bytearray:
        return hash(self.envelope())

    def json(self) -> typing.Dict:
        return {
            'chain_id': self.chain_id,
            'nonce': self.nonce,
            'gas_price': self.gas_price,
            'gas': self.gas,
            'to': self.to.hex() if self.to else None,
            'value': self.value,
            'data': self.data.hex(),
            'access_list': [[e[0].hex(), [f.hex() for f in e[1]]] for e in self.access_list],
            'v': self.v,
            'r': self.r,
            's': self.s,
        }

    def sign(self, prikey: PriKey) -> None:
        sign = prikey.sign(hash(bytearray([0x01]) + pleth.rlp.encode([
            pleth.rlp.put_uint(self.chain_id),
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_price),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            self.access_list,
        ])))
        self.r = int.from_bytes(sign[0x00:0x20])
        self.s = int.from_bytes(sign[0x20:0x40])
        # TxAccessList are defined to use 0 and 1 as their recovery.
        # Why EIP-2930 access list tx use unprotected Homestead signature scheme?
        # See also: https://github.com/ethereum/go-ethereum/issues/24421.
        self.v = sign[0x40]


class TxDynamicFee:
    # TxDynamicFee represents an EIP-1559 transaction.
    # See https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md.
    def __init__(
        self,
        nonce: int,
        gas_tip_cap: int,  # a.k.a. max_priority_fee_per_gas
        gas_fee_cap: int,  # a.k.a. max_fee_per_gas
        gas: int,
        to: typing.Optional[bytearray],
        value: int,
        data: bytearray,
    ) -> None:
        assert isinstance(data, bytearray)
        self.chain_id = pleth.config.current.chain_id
        self.nonce = nonce
        self.gas_tip_cap = gas_tip_cap
        self.gas_fee_cap = gas_fee_cap
        self.gas = gas
        self.to = to
        self.value = value
        self.data = data
        self.access_list = []
        self.v = 0
        self.r = 0
        self.s = 0

    def __eq__(self, other) -> bool:
        return self.hash() == other.hash()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def envelope(self) -> bytearray:
        return bytearray([0x02]) + pleth.rlp.encode([
            pleth.rlp.put_uint(self.chain_id),
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_tip_cap),
            pleth.rlp.put_uint(self.gas_fee_cap),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            self.access_list,
            pleth.rlp.put_uint(self.v),
            pleth.rlp.put_uint(self.r),
            pleth.rlp.put_uint(self.s),
        ])

    def hash(self) -> bytearray:
        return hash(self.envelope())

    def json(self) -> typing.Dict:
        return {
            'chain_id': self.chain_id,
            'nonce': self.nonce,
            'gas_tip_cap': self.gas_tip_cap,
            'gas_fee_cap': self.gas_fee_cap,
            'gas': self.gas,
            'to': self.to.hex() if self.to else None,
            'value': self.value,
            'data': self.data.hex(),
            'access_list': [[e[0].hex(), [f.hex() for f in e[1]]] for e in self.access_list],
            'v': self.v,
            'r': self.r,
            's': self.s,
        }

    def sign(self, prikey: PriKey) -> None:
        sign = prikey.sign(hash(bytearray([0x02]) + pleth.rlp.encode([
            pleth.rlp.put_uint(self.chain_id),
            pleth.rlp.put_uint(self.nonce),
            pleth.rlp.put_uint(self.gas_tip_cap),
            pleth.rlp.put_uint(self.gas_fee_cap),
            pleth.rlp.put_uint(self.gas),
            self.to if self.to else bytearray(),
            pleth.rlp.put_uint(self.value),
            self.data,
            self.access_list,
        ])))
        self.r = int.from_bytes(sign[0x00:0x20])
        self.s = int.from_bytes(sign[0x20:0x40])
        self.v = sign[0x40]


class Text:
    def __init__(self, data: str) -> None:
        self.data = data

    def hash(self) -> bytearray:
        # TextHash is a helper function that calculates a hash for the given message that can be safely used to
        # calculate a signature from. The hash is calculated as
        # keccak256("\x19Ethereum Signed Message:\n"${message length}${message}).
        # Note that message length is a string representation of the length.
        # See https://pkg.go.dev/github.com/ethereum/go-ethereum@v1.14.7/accounts#TextHash
        data = '\x19Ethereum Signed Message:\n'
        data += str(len(self.data))
        data += self.data
        return pleth.core.hash(data.encode())

    def pubkey(self, sig: bytearray) -> PubKey:
        m = pleth.secp256k1.Fr(int.from_bytes(self.hash()))
        r = pleth.secp256k1.Fr(int.from_bytes(sig[0x00:0x20]))
        s = pleth.secp256k1.Fr(int.from_bytes(sig[0x20:0x40]))
        v = (sig[0x40] - 27) % 4
        return PubKey.pt_decode(pleth.ecdsa.pubkey(m, r, s, v))

    def sign(self, prikey: PriKey) -> bytearray:
        # Presents a plain text signature challenge to the user and returns the signed response.
        sig = prikey.sign(self.hash())
        sig[0x40] += 27
        return sig
