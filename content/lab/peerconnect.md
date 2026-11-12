+++

title = "PeerConnect"
date = 2026-11-12

+++

简单描述一下这个项目

**两个应用，一个房间。中继什么也读不到。** PeerConnect 是一个开放协议，通过 WebSocket 中继给两个应用建立私密、可靠的通道。中继既读不到、也伪造或重放不了它们之间的任何消息，而且什么都不存储。

网站：https://peerconnect.dev/

## 用在哪里

- 钱包 ↔ 网页应用
- 手机 ↔ 电脑
- 设备 ↔ 设备
- 你 ↔ 你自己的服务（服务在 NAT 后面，不用开端口）

和 WebRTC 比：不需要信令、STUN、TURN，始终走普通的 WebSocket 中继，另外还提供配对、持久身份和可靠投递。和 WalletConnect 比：它是通用的，不只服务钱包。

## 特点

- **不信任中继**：端到端加密并认证，中继只能看到消息大小和时间，看不到内容和密钥。
- **无状态**：没有数据库，房间只在双方连着时存在。
- **可靠、有序、恰好一次**：消息编号、确认，断线后重发。发送方自己就是队列。
- **邀请会过期**：配对完成后双方换到新的配对 ID，泄露的二维码或链接就没用了。
- **任何语言都能实现**：公开规范 + 测试向量，还提供 `llms.txt` 让 AI agent 照着实现。

## 原理

1. 邀请方随机生成 32 字节的房间密钥 S，由它派生出 psk、邀请 ID 和房间 ID。
2. 邀请是 `中继地址#base64url(S ‖ 邀请方身份公钥)`，用二维码、链接或粘贴的方式交给对方。
3. 加入方用 Ed25519 签名中继下发的 nonce，然后双方跑一次 `Noise_IKpsk1_25519_ChaChaPoly_SHA256` 握手；邀请方记住加入方的身份，双方换到由 X25519 共享密钥算出的配对 ID。
4. 之后的消息用 ChaCha20-Poly1305 加密，单帧最大 64 KiB，单条消息最大 16 MiB，断线可以续传。

协议提供机密性、完整性、双向认证、前向保密和身份隐藏，但不保证可用性。

## 快速上手

没有 SDK，拿到 token 后按规范实现自己这一端：

```sh
# 试用 token，不用注册，有效两小时
curl -X POST https://peerconnect.dev/api/trial

# 每个端用自己的 token 连接
# wss://relay.peerconnect.dev/v1/<room id>?token=<token>
```

中继也可以自己部署：Cloudflare Workers（每个房间一个 Durable Object）、Docker，或者 `cargo install peerconnect-relay`。

## 状态

协议还是 v1 草案，测试很充分但没有经过外部审计，线上格式可能还会变，暂时不要用来保护高价值资产。公共中继只用于测试，不保证可用性。

## 开源

MIT 协议：[github.com/atshelchin/peerconnect](https://github.com/atshelchin/peerconnect)，包含 Rust 参考实现（无 I/O 的状态机）、编译成 WebAssembly 的 JS 版本和测试向量。
