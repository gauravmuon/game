// SPDX-License-Identifier: BUSL-1.1

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BulkTransfer is Ownable {
    using SafeERC20 for IERC20;

    function transfer(
        address tokenAddress,
        address[] memory recipients,
        uint[] memory amounts
    ) public onlyOwner {
        require(recipients.length == amounts.length, "Invalid input");
        IERC20 token = IERC20(tokenAddress);
        for (uint i = 0; i < recipients.length; i++) {
            token.transferFrom(msg.sender, recipients[i], amounts[i]);
        }
    }
}
