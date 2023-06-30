// SPDX-License-Identifier: BUSL-1.1
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

pragma solidity ^0.8.4;

interface IRouter {
    struct TradeParams {
        bytes poolId;
        uint256 queueId;
        string avatarUrl;
        string countryCode;
        bool upOrDown;
        string whiteLabelId;
        address trader;
        bytes signature;
        uint256 signatureTimestamp;
        address targetContract;
    }


    struct AccountMapping {
        address oneCT;
        uint256 nonce;
    }

    struct QueuedTrade {
        uint256 queueId;
        bytes poolId;
        string avatarUrl;
        string countryCode;
        bool upOrDown;
        string whiteLabelId;
        address trader;
        bytes signature;
        uint256 signatureTimestamp;
    }

    struct OpenTradeStruct {
        bytes poolId;
        string avatarUrl;
        string countryCode;
        bool upOrDown;
        string whiteLabelId;
        address trader;
    }

    event RegisterAccount(address indexed account, address indexed oneCT);
    event ContractRegistryUpdated(address targetContract, bool register);
    event FailResolve(uint256 queueId, string reason);
    event CancelTrade(address indexed account, uint256 queueId, string reason);
    event OpenTrade(
        address indexed account,
        uint256 queueId,
        address targetContract
    );

    struct CloseTradeParams {
        uint256 optionId;
        address targetContract;
        uint256 expiryTimestamp;
        uint256 priceAtExpiry;
        bytes signature;
    }
    event FailUnlock(address targetContract, string reason);
}

interface IUpVsDownGame {
    struct makeTradeStruct {
        bytes poolId;
        string avatarUrl;
        string countryCode;
        bool upOrDown;
        string whiteLabelId;
        address trader;
    }

    struct userDataStruct {
        string avatar;
        string countryCode;
        string whiteLabelId;
        int64 roundStartTime;
    }

    function asset() external view returns (string memory);

    function trigger(
        bytes calldata poolId,
        int64 timeMS,
        uint256 tradesStartTimeMS,
        uint256 tradesEndTimeMS,
        int32 price,
        uint32 batchSize
    ) external;

    function makeTrade(makeTradeStruct calldata) external;
}
