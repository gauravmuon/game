// SPDX-License-Identifier: BUSL-1.1

pragma solidity 0.8.4;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../interfaces/Interfaces.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @author Heisenberg
 * @notice Buffer Options Router Contract
 */
contract Router is AccessControl, IRouter {
    address public publisher;
    address public admin;
    bool public isInPrivateKeeperMode = true;

    mapping(uint256 => QueuedTrade) public queuedTrades;
    mapping(address => bool) public contractRegistry;
    mapping(address => bool) public isKeeper;
    mapping(address => AccountMapping) public accountMapping;
    mapping(bytes => bool) public prevSignature;

    constructor(address _publisher, address _admin) {
        publisher = _publisher;
        admin = _admin;
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /************************************************
     *  ADMIN ONLY FUNCTIONS
     ***********************************************/

    function setContractRegistry(
        address targetContract,
        bool register
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        contractRegistry[targetContract] = register;

        emit ContractRegistryUpdated(targetContract, register);
    }

    function setKeeper(
        address _keeper,
        bool _isActive
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        isKeeper[_keeper] = _isActive;
    }

    function setInPrivateKeeperMode() external onlyRole(DEFAULT_ADMIN_ROLE) {
        isInPrivateKeeperMode = !isInPrivateKeeperMode;
    }

    /************************************************
     *  USER WRITE FUNCTIONS
     ***********************************************/

    function registerAccount(address oneCT) external {
        accountMapping[msg.sender].oneCT = oneCT;
        emit RegisterAccount(msg.sender, oneCT);
    }

    function deregisterAccount() external {
        accountMapping[msg.sender] = AccountMapping({
            nonce: accountMapping[msg.sender].nonce + 1,
            oneCT: address(0)
        });
    }

    /************************************************
     *  BASE INTERNAL FUNCTIONS
     ***********************************************/
    function _validateKeeper() private view {
        require(
            !isInPrivateKeeperMode || isKeeper[msg.sender],
            "Keeper: forbidden"
        );
    }

    function _validate(
        bytes32 hashData,
        bytes memory expectedSignature,
        address expectedSigner
    ) internal pure returns (bool) {
        bytes32 digest = ECDSA.toEthSignedMessageHash(hashData);
        (address recoveredSigner, ECDSA.RecoverError error) = ECDSA.tryRecover(
            digest,
            expectedSignature
        );
        if (error == ECDSA.RecoverError.NoError) {
            return recoveredSigner == expectedSigner;
        } else {
            return false;
        }
    }

    /************************************************
     *  KEEPER ONLY FUNCTIONS
     ***********************************************/

    function openTrades(TradeParams[] calldata params) external {
        _validateKeeper();
        for (uint32 index = 0; index < params.length; index++) {
            TradeParams memory currentParams = params[index];
            (bool isValid, string memory errorReason) = _verifyTrade(
                currentParams
            );
            if (!isValid) {
                emit FailResolve(currentParams.queueId, errorReason);
                continue;
            }
            _openTrade(currentParams);
        }
    }

    function GameTrigger(
        bytes calldata poolId,
        int64 timeMS,
        uint256 tradesStartTimeMS,
        uint256 tradesEndTimeMS,
        int32 price,
        uint32 batchSize,
        address targetContract,
        bytes memory publisherSignature,
        uint256 publisherSignatureTimestamp
    ) public {
        _validateKeeper();
        IUpVsDownGame gameContract = IUpVsDownGame(targetContract);
        bytes32 hashData = keccak256(
            abi.encodePacked(
                gameContract.asset(),
                publisherSignatureTimestamp,
                price,
                publisher
            )
        );
        // Silently fail if the signature doesn't match
        if (!_validate(hashData, publisherSignature, publisher)) {
            emit FailUnlock(targetContract, "Router: Signature didn't match");
        }
        gameContract.trigger(
            poolId,
            timeMS,
            tradesStartTimeMS,
            tradesEndTimeMS,
            price,
            batchSize
        );
    }

    /************************************************
     *  INTERNAL FUNCTIONS
     ***********************************************/

    function _verifyTrade(
        TradeParams memory params
    ) public view returns (bool, string memory) {
        if (prevSignature[params.signature]) {
            return (false, "Router: Signature already used");
        }
        bytes32 hashData = keccak256(
            abi.encodePacked(
                params.poolId,
                params.queueId,
                params.avatarUrl,
                params.countryCode,
                params.upOrDown,
                params.whiteLabelId,
                params.trader
            )
        );
        if (!_validate(hashData, params.signature, params.trader)) {
            return (false, "Router: User signature didn't match");
        }
        return (true, "");
    }

    function _openTrade(TradeParams memory params) internal {
        IUpVsDownGame gameContract = IUpVsDownGame(params.targetContract);
        OpenTradeStruct memory tradeParams = OpenTradeStruct({
            poolId: params.poolId,
            avatarUrl: params.avatarUrl,
            countryCode: params.countryCode,
            upOrDown: params.upOrDown,
            whiteLabelId: params.whiteLabelId,
            trader: params.trader
        });

        IUpVsDownGame.makeTradeStruct memory tradeStruct = IUpVsDownGame
            .makeTradeStruct({
                poolId: params.poolId,
                avatarUrl: params.avatarUrl,
                countryCode: params.countryCode,
                upOrDown: params.upOrDown,
                whiteLabelId: params.whiteLabelId,
                trader: params.trader
            });
        gameContract.makeTrade(tradeStruct);
        queuedTrades[params.queueId] = QueuedTrade({
            queueId: params.queueId,
            poolId: params.poolId,
            avatarUrl: params.avatarUrl,
            countryCode: params.countryCode,
            upOrDown: params.upOrDown,
            whiteLabelId: params.whiteLabelId,
            trader: params.trader,
            signature: params.signature,
            signatureTimestamp: params.signatureTimestamp
        });

        prevSignature[params.signature] = true;

        emit OpenTrade(params.trader, params.queueId, params.targetContract);
    }
}
