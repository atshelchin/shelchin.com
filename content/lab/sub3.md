+++
title = "sub3.dev"
date = 2025-10-14
updated = 2026-11-12

+++

简单描述一下这个项目

sub3 是链上的极简 Stripe：给开发者做的钱包登录 + 稳定币收款，跑在 Arc 链上，用 USDC 付款。

网站：https://sub3.dev

## 怎么用

1. 开发者在 [sub3.dev/dashboard](https://sub3.dev/dashboard) 注册一个永久商号（handle），建产品，在产品下面定价。
2. 给自己的 coding agent 一句话：

   > Add sub3 to this app for my product `acme/app`, following https://sub3.dev/llms.txt.

3. 应用只需要打开 sub3 的托管页（登录 `/login`、结账 `/checkout`），再调一个 HTTP 接口 `/v1/access` 判断用户有没有权限。扫码、手机钱包连接、付款都在托管页里完成。

## 能卖的三种东西

| 类型 | 价格 | 规则 |
|---|---|---|
| **档位订阅（Tier）** | 按月定价，年付 = 12 个月按 10 个月收费 | 每个用户在一个产品下只有一个档位；随时续费；可以立刻升到更高档（当前档剩余时间作废）；降档要等到期 |
| **买断（Lifetime）** | 一次性 | 永久拥有，和档位互不影响 |
| **积分包（Pack）** | 按包定价，每包若干积分 | 可以重复购买，商户按收据给用户记积分 |

只有手动续费，不自动扣款，也不代付 gas。

## 收费方式

- 每笔付款收 1% + $0.05，在同一笔交易里直接拆给商户和 sub3 的 treasury（Safe 多签）。
- 注册商号一次性 $20。

## 设计原则

- **链上是唯一的真相**：商号、产品、价格、会员、订单凭证、统计都在合约里。后端只读链、验签、缓存，没有数据库。
- **合约没有 owner**：不可升级、不能暂停、不托管资金（余额恒为 0，有不变量测试保证）。要改规则只能部署新版本合约，旧合约永远可读。
- **身份靠商号，不靠钱包**：handle 永久不变，钱包、收款地址、网站都可以换。防冒充靠域名验证（`/.well-known/sub3.json`）。
- 链上统计实时公开：[sub3.dev/stats](https://sub3.dev/stats)。

## 环境

| 环境 | 链 | 地址 |
|---|---|---|
| 正式 | Arc 主网（5042） | https://sub3.dev |
| 沙盒 | Arc 测试网（5042002），测试 USDC 从 [Circle Faucet](https://faucet.circle.com) 领 | https://sub3.dev/sandbox |

接入建议先在沙盒跑通，沙盒和正式环境是同一份代码，但会话、订单、积分完全隔离。

## 合约

`Sub3Checkout` 通过 CREATE2 部署，在 Arc 主网和测试网是同一个地址：

`0x5F7c7E293F3EaDBc730EF62Cf9B6ee11f2d60dF7`

- Arc 主网：https://explorer.arc.io/address/0x5F7c7E293F3EaDBc730EF62Cf9B6ee11f2d60dF7
- Arc 测试网：https://explorer.testnet.arc.io/address/0x5F7c7E293F3EaDBc730EF62Cf9B6ee11f2d60dF7

项目仓库不开源，合约源码已在 Arc 区块链浏览器上验证公开，可以直接在上面阅读和核对。

## 文档

- 接入规范（v1，已冻结）：https://sub3.dev/spec
- 给 agent 读的接入指南：https://sub3.dev/llms.txt
- 合约 ABI：https://sub3.dev/abi.json
