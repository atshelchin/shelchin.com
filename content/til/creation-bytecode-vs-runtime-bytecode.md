+++
title = "Creation Bytecode vs Runtime Bytecode"
date = 2025-11-06

+++


> Understanding the difference between creation and runtime bytecode is crucial for contract deployment and analysis.



## TL;DR

```
Deployment Input = Creation Bytecode + Constructor Args (ABI-encoded)
                   └─ From compiler    └─ You append this
```

**Creation bytecode does NOT include constructor arguments.**

## Quick Reference

| Bytecode Type | Contains | Use Case |
|--------------|----------|----------|
| Creation | Init logic + Runtime code | `forge inspect Contract bytecode` |
| Runtime | Final on-chain code | `cast code <address>` |

## Deployment Hex Pattern

```
0x[CREATION_CODE][CONSTRUCTOR_ARGS]
  └─ Fixed length  └─ Variable (32 bytes per param)
```

### Example

```bash
# Contract: constructor(uint256 supply, address owner)

CREATION=$(forge inspect MyToken bytecode)
# 0x608060405234801561001057600080fd5b50...

ARGS=$(cast abi-encode "constructor(uint256,address)" 1000000 0x742d35Cc6634C0532925a3b844Bc454e4438f44e)
# 0x00000000000000000000000000000000000000000000000000000000000f4240
#   000000000000000000000000742d35cc6634c0532925a3b844bc454e4438f44e

# Deploy (remove 0x from args)
cast send --create "${CREATION}${ARGS:2}" --rpc-url <RPC> --private-key <KEY>
```

### Hex Breakdown

```
0x608060405234801561001057600080fd5b50...  ← Creation bytecode
  00000000000000000000000000000000000000000000000000000000000f4240  ← uint256 (32 bytes)
  000000000000000000000000742d35cc6634c0532925a3b844bc454e4438f44e  ← address (32 bytes, left-padded)
```

## Clone Existing Contract

Deployment tx input already has both parts - use directly:

```bash
# 1. Find deployment tx (Etherscan/Sourcify)
# 2. Extract full bytecode
FULL=$(cast tx <DEPLOY_TX> input --rpc-url <RPC>)

# 3. Deploy (args already included)
cast send --create $FULL --rpc-url http://localhost:8545 --private-key <KEY>
```

### Example: Multicall3

```bash
# Contract: 0xcA11bde05977b3631167028862bE2a173976CA11
# No constructor args - only creation bytecode

TX="0x4f0a3c5bb2dcb0420c54838830c894f09e10f0e59d91b0d19cb2d4c234cb2c2f"
BYTECODE=$(cast tx $TX input --rpc-url https://eth.llamarpc.com)

cast send --create $BYTECODE --rpc-url http://localhost:8545 --private-key <KEY>
```

## Common Mistakes

```bash
# ❌ Using runtime bytecode
cast send --create $(cast code 0xAddress)

# ❌ Forgetting constructor args
cast send --create $(forge inspect MyContract bytecode)

# ❌ Not removing 0x prefix
DEPLOY="${CREATION}${ARGS}"  # Double 0x

# ✅ Correct
DEPLOY="${CREATION}${ARGS:2}"
```

## Key Points

1. **Creation ≠ Deployment**
   - Compiler outputs creation bytecode
   - You must append ABI-encoded constructor args

2. **Constructor args pattern**
   - Each `uint256`/`address` = 32 bytes (64 hex chars)
   - Addresses are left-padded with zeros

3. **Cloning contracts**
   - Get deployment tx input via Sourcify/Etherscan
   - Contains both creation code + args, ready to use

4. **Why `cast creation` fails**
   - Needs RPC trace APIs (rarely available)
   - Use block explorers instead

## Resources

- [Sourcify](https://sourcify.dev) - Find deployment transactions
- [Etherscan](https://etherscan.io) - Contract creation info
- [Solidity Docs: Contract Creation](https://docs.soliditylang.org/en/latest/introduction-to-smart-contracts.html#creating-contracts)
- [EVM Bytecode](https://ethervm.io/)
- [Foundry Book: Cast Reference](https://getfoundry.sh/cast/reference/cast)