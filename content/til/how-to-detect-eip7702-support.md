+++
title = "How to Detect EIP-7702 Support with a Single RPC Call"
date = 2025-10-15

+++



> Quick test to check if any Ethereum network supports EIP-7702 account abstraction.

## The Problem

With EIP-7702 rolling out (enabled on Ethereum mainnet via Pectra upgrade), you need to know which networks support it before building. Traditional methods require complex setup or waiting for official announcements.

## The Solution

Use `eth_estimateGas` with state override to probe for EIP-7702 support:

```bash
curl https://your-rpc-endpoint.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_estimateGas",
    "params": [
      {
        "from": "0xdeadbeef00000000000000000000000000000000",
        "to": "0xdeadbeef00000000000000000000000000000000",
        "data": "0x00",
        "value": "0x0"
      },
      "latest",
      {
        "0xdeadbeef00000000000000000000000000000000": {
          "code": "0xef01000000000000000000000000000000000000000001"
        }
      }
    ],
    "id": 1
  }'
```

## How It Works

1. **State override** temporarily sets code `0xef01...0001` for a dummy address
2. **`0xef01` prefix** is EIP-7702's magic delegation designator
3. **Unsupported nodes** reject `0xef` as invalid opcode
4. **Supported nodes** recognize delegation and return gas estimate

## Reading Results

### ✅ Supported

```json
{
  "jsonrpc": "2.0",
  "result": "0x5875"
}
```

### ❌ Not Supported

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "invalid opcode: opcode 0xef not defined"
  }
}
```

## Why This Works

- **`0xef01`**: EIP-7702 delegation designator format
- **Target `0x01`**: ecrecover precompile (exists on all EVM chains)
- **From = To**: Simulates EOA calling itself (core EIP-7702 pattern)
- **State override**: Tests without actual deployment

## Verified Networks

- ✅ Ethereum Mainnet (Pectra upgrade)
- ✅ BNB Chain Mainnet
- ✅ Polygon PoS (Bhilai hardfork)
- ❌ opBNB Mainnet (invalid opcode: opcode 0xef not defined @2025.10.15)
- ❌ Linea ( invalid opcode: opcode 0xef not defined  @2025.10.15)



------

**Related**: EIP-7702, Account Abstraction, Smart EOAs, Ethereum Pectra Upgrade, State Override Testing

