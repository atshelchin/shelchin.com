+++

title = "Vela Wallet（原 keyper 钱包）"
date = 2025-10-29
updated = 2026-11-12

+++

简单描述一下这个项目

原来叫 keyper 的 AA 钱包现在叫 **Vela Wallet**（keyper 这个名字和 getkeyper.app 现在给了[另一个项目](@/lab/memory-vault.md)）。

**真正属于你的以太坊钱包，没有助记词。** 签名在你自己的设备上完成，passkey 私钥从不经过 Vela。

官网：https://getvela.app/ ，目前处于 Alpha 阶段。

## 账户

- 账户是一个**未经修改的 Safe v1.4.1**，通过 ERC-4337（EntryPoint v0.7 + Safe4337Module v0.3.0）使用，资金路径上没有 Vela 自己的合约。
- 签名密钥是 passkey（WebAuthn，P-256 曲线），由链上的 EIP-7951 / RIP-7212 预编译合约验签。
- 地址用 CREATE2 算出，在每条链上都一样。
- 创建时可以设置最多 7 把密钥，任意一把都能单独签名（1-of-n），创建后不能增删：
  - 本机 passkey（Face ID / Touch ID，通过 iCloud 钥匙串或 Google 密码管理器同步）
  - 附近的另一台手机（扫码）
  - 硬件安全密钥（FIDO2，比如 YubiKey）

## 恢复

不用助记词、邮箱或守护人。恢复只靠两样东西：一把你还留着的密钥，加上一份公开的记录，写明哪些密钥属于你的钱包。

- 创建钱包时，这份记录会写进 Gnosis Chain 上的一个公开注册合约（没有 owner，不可升级），也可以再复制一份到以太坊主网。
- 换设备时，用任意一把密钥登录就能找回钱包。
- 所有密钥都丢了就没有人能恢复，Vela、Apple、Google 都不行。Vela 也无法转走你的资金或冻结钱包。

## 交易与费用

- App 构造 UserOperation，你签名，由 relay 上链并垫付 gas；手续费作为同一个批次里的一笔转账付给 relay，没有 paymaster，也没有人替你付 gas。
- 手续费 = 3 × 预留 gas × gas 价格，最低约 $0.01，签名前会显示金额。可以用链的原生币付，也可以用 relay 接受的美元稳定币付。
- 默认用 Vela 的 relay，也可以换成别人的或自己部署的 [vela-relay](https://github.com/mondaylabsltd/vela-relay)。
- "所见即所签"：批准前会解码交易内容。
- 内置 24 条主网（Ethereum、Base、Arbitrum、Optimism、Polygon、BNB Chain、Gnosis、Arc 等），也可以添加支持 P-256 预编译的自定义 EVM 网络。

## 平台

- **网页钱包（推荐）**：https://wallet.getvela.app/ ，免安装，但不能连接 dApp。
- **浏览器扩展**（Chrome / Edge / Brave）：Chrome 应用商店即将上架，现在可以下载后手动加载。
- **桌面端**：Windows、macOS、Linux。
- **iOS / Android**：正在真机测试，App Store 和 Google Play 即将上架；也可以自己从源码编译。

网页版、扩展、桌面端和自己编译的手机 App 都免费；商店里的手机 App 会一次性买断收费，用来支持开发。

## 开源

所有 App 和服务都以 MIT 协议开源：

- 钱包：https://github.com/mondaylabsltd/vela-wallet
- Relay：https://github.com/mondaylabsltd/vela-relay
- Passkey 公钥索引：https://github.com/mondaylabsltd/p256-index

Safe、Safe4337Module、SafeWebAuthn 和 EntryPoint 这些合约都经过了第三方审计；Vela 自己的代码（App、后端服务和注册合约）还没有审计，也没有排期。
