import io
import pleth.core
import pleth.io

# The Contract Application Binary Interface (ABI) is the standard way to interact with contracts in the Ethereum
# ecosystem, both from outside the blockchain and for contract-to-contract interaction. Data is encoded according to
# its type, as described in this specification. The encoding is not self describing and thus requires a schema in order
# to decode.
#
# See: https://docs.soliditylang.org/en/latest/abi-spec.html


def function_selector(name: str, args_type: list[str]) -> bytearray:
    s = name + '(' + ','.join(args_type) + ')'
    return pleth.core.hash(bytearray(s.encode()))[:4]


def argument_encoding(data: list[bytearray]) -> bytearray:
    s = bytearray()
    for e in data:
        s.extend(e)
    return s


class Address:
    @classmethod
    def decode(cls, reader: io.IOBase) -> bytearray:
        return pleth.io.read_full(reader, 32)[12:]

    @classmethod
    def encode(cls, origin: bytearray) -> bytearray:
        assert len(origin) == 20
        return bytearray(12) + origin


class Bytes:
    @classmethod
    def decode(cls, reader: io.IOBase) -> bytearray:
        length = Uint256.decode(reader)
        padded = (length + 31) & -32
        return pleth.io.read_full(reader, padded)[:length]

    @classmethod
    def encode(cls, origin: bytearray) -> bytearray:
        length = len(origin)
        padded = (length + 31) & -32
        return Uint256.encode(length) + origin + bytearray(padded - length)


class String:
    @classmethod
    def decode(cls, reader: io.IOBase) -> str:
        return Bytes.decode(reader).decode()

    @classmethod
    def encode(cls, origin: str) -> bytearray:
        return Bytes.encode(bytearray(origin.encode()))


class Uint256:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pleth.io.read_full(reader, 32), 'big')

    @classmethod
    def encode(cls, origin: int) -> bytearray:
        assert origin >= 0
        assert origin <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return bytearray(origin.to_bytes(32, 'big'))
