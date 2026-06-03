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


def argument_decoding(args_type: list, data: bytearray) -> list:
    return Tuple(args_type).decode(io.BytesIO(data))


def argument_encoding(args_type: list, args: list) -> bytearray:
    return Tuple(args_type).encode(args)


class Address:
    @classmethod
    def decode(cls, reader: io.IOBase) -> bytearray:
        return pleth.io.read_full(reader, 32)[12:]

    @classmethod
    def encode(cls, origin: bytearray) -> bytearray:
        assert len(origin) == 20
        return bytearray(12) + origin

    @classmethod
    def size(cls) -> int:
        return 32


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

    @classmethod
    def size(cls) -> int:
        return 0


class String:
    @classmethod
    def decode(cls, reader: io.IOBase) -> str:
        return Bytes.decode(reader).decode()

    @classmethod
    def encode(cls, origin: str) -> bytearray:
        return Bytes.encode(bytearray(origin.encode()))

    @classmethod
    def size(cls) -> int:
        return 0


class Tuple:
    def __init__(self, kype: list) -> None:
        self.kype = kype
        self.slen = 0
        size_list = [k.size() for k in kype]
        if all([s != 0 for s in size_list]):
            self.slen = sum(size_list)

    def decode(self, reader: io.IOBase) -> list:
        muts = []
        vals = []
        for k in self.kype:
            match k.size():
                case 0:
                    muts.append(len(vals))
                    vals.append(Uint256.decode(reader))
                case _:
                    vals.append(k.decode(reader))
        for i in muts:
            vals[i] = self.kype[i].decode(reader)
        return vals

    def encode(self, origin: list) -> bytearray:
        assert len(origin) == len(self.kype)
        offs = 0
        for k in self.kype:
            offs += 32 if k.size() == 0 else k.size()
        head = bytearray()
        tail = bytearray()
        for k, v in zip(self.kype, origin):
            e = k.encode(v)
            match k.size():
                case 0:
                    head.extend(Uint256.encode(offs + len(tail)))
                    tail.extend(e)
                case _:
                    head.extend(e)
        return head + tail

    def size(self) -> int:
        return self.slen


class Uint256:
    @classmethod
    def decode(cls, reader: io.IOBase) -> int:
        return int.from_bytes(pleth.io.read_full(reader, 32), 'big')

    @classmethod
    def encode(cls, origin: int) -> bytearray:
        assert origin >= 0
        assert origin <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return bytearray(origin.to_bytes(32, 'big'))

    @classmethod
    def size(cls) -> int:
        return 32
