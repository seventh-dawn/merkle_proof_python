//SPDX-License-Identifier: MIT
pragma solidity 0.8.7;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract MerkleAirdrop is Ownable{
    // This is a packed array of booleans.
    bytes32 public root;

    // This event is triggered whenever a call to #claim succeeds.
    mapping(address => bool) private claimedAddresses;

    IERC20 public token;

    event Claimed(address account, uint256 amount);
    constructor(IERC20 _token) {
        token = _token;
    }

    function testProof(
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    )
        public
        returns (bool)
    {
        bytes32 node = keccak256(abi.encodePacked(account, amount));
        return MerkleProof.verify(merkleProof, root, node);
    }

    function claim(
        address account,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) external {
        // Verify the merkle proof.
        bytes32 node = keccak256(abi.encodePacked(account, amount));
        require(!claimedAddresses[account], "Drop already claimed.");
        require(MerkleProof.verify(merkleProof, root, node), "Invalid proof.");

        // Mark it claimed and send the token.
        claimedAddresses[account] = true;
        token.transfer(account, amount);

        emit Claimed(account, amount);
    }

    function setRoot(bytes32 _root) external onlyOwner {
        root = _root;
    }
}
