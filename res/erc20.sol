// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Pleth is ERC20 {
    // Constructor mints all initial supply to the deployer's wallet
    // 1,000,000 tokens * 10^18 decimals standard
    constructor() ERC20("Pleth", "Pleth") {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
}
