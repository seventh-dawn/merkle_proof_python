from abc import ABC, abstractmethod
import random
from typing import Callable, Optional

from brownie import web3



class Leaf(ABC):
    index: int
    @property
    @abstractmethod
    def hex_value(self)->str:
        pass

class LeafData(Leaf):
    account: str
    amount: int

    def __init__(self, index, account, amount):
        self.index = index
        self.account = account.replace("0x", "").zfill(40)
        self.amount = amount

    @property
    def hex_value(self):
        amount = self.amount
        if isinstance(amount, int):
            amount = hex(amount).replace('0x', '').zfill(64)
        else:
            amount = amount.replace("0x", "").zfill(64)
        return f"{self.account}{amount}"


def pad_hex(hex_str, length=64):
    return hex_str.replace("0x", "").zfill(length)


def concat_hex(*args):
    return "".join([pad_hex(arg) for arg in args])

def kekkak(x):
    # print(x)
    x = x.replace("0x", "")
    return web3.sha3(hexstr=x).hex()

class MerkleTree:
    data: list[Leaf]
    hash_func: Optional[Callable[[str], str]]
    parent: Optional["MerkleTree"]
    leaf: Optional[Leaf]
    left: Optional["MerkleTree"]
    right: Optional["MerkleTree"]
    hash: Optional[str]
    index: Optional[int]
    cutoff: Optional[int]
    size: int
    def __init__(self, data, hash_func: Callable[[str], str]=kekkak, parent=None):
        self.data = data
        self.data.sort(key=lambda x: x.index)
        self.hash_func = hash_func
        self.parent = parent
        self.leaf = None
        self.left = None
        self.right = None
        self.hash = None
        self.index = None
        self.cutoff = None
        self._build()

    def _build(self):
        self.size = len(self.data)
        if len(self.data) == 1:
            self.leaf = self.data[0]
            self.hash = self.hash_func(self.leaf.hex_value)
            return

        left_data = self.data[: len(self.data) // 2]
        right_data = self.data[len(self.data) // 2 :]
        self.cutoff = max([leaf.index for leaf in left_data])

        if len(left_data) > 0:
            self.left = MerkleTree(left_data, self.hash_func, self)
        if len(right_data) > 0:
            self.right = MerkleTree(right_data, self.hash_func, self)

        print(self.left.hash, self.right.hash)
        
        print(type(self.left.hash), type(self.right.hash))
        if self.left is None:
            self.hash = self.right.hash
        elif self.right is None:
            self.hash = self.left.hash
        elif int(self.left.hash, 16) <= int(self.right.hash, 16):
            self.hash = self.hash_func(self.left.hash + self.right.hash)
        elif int(self.left.hash, 16) > int(self.right.hash, 16):
            self.hash = self.hash_func(self.right.hash + self.left.hash)
    @property
    def is_root(self):
        return self.parent is None

    def get_proof(self, node_index):
        if node_index>= self.size and self.is_root:
            raise ValueError("Node index out of range")
        if self.leaf is not None:
            assert self.leaf.index == node_index
            return []

        if node_index <= self.cutoff:
            if self.right is not None:
                proof = [self.right.hash] + self.left.get_proof(node_index)
            else:
                proof =  self.left.get_proof(node_index)
        else:
            if self.left is not None:
                proof = [self.left.hash] + self.right.get_proof(node_index)
            else:
                proof = self.right.get_proof(node_index)
        if self.is_root:
            return list(reversed(proof))
        return proof


    def dump(self):
        if self.leaf is not None:
            return (self.leaf.amount, self.leaf.account, self.leaf.index)
        return {"left": self.left.dump(), "right": self.right.dump()}

    def test_proof(self, node_value, proof):
        node_value = self.hash_func(node_value)
        for element in proof:
            if int(element, 16) > int(node_value, 16):
                node_value = self.hash_func(node_value + element)
            else:
                node_value = self.hash_func(element + node_value)
            # print(node_value)
        return node_value == self.hash





def get_random_address():
    characters = [str(i) for i in list(range(0, 10)) + ["A", "B", "C", "D", "E", "F"]]
    return web3.toChecksumAddress("0x" + "".join([random.choice(characters) for _ in range(0, 40)]))
# import json
# # values = {get_random_address(): random.randint(0, 10**22) for _ in range(0, 5)}
# # json.dump(values, open("values.json", "w"))
# values = json.load(open("values.json", "r"))
# leaves = [LeafData(i, account, amount) for i, (account, amount) in enumerate(values.items())]
# tree = MerkleTree(leaves, kekkak)
# tree.get_proof(0)
