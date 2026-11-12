+++

title = "ClientMCP"
date = 2026-11-12

+++

简单描述一下这个项目

**UI for humans. MCP for agents.** 把一个正在运行的浏览器、桌面或手机应用，暴露成一个标准的 MCP server。agent 调用的就是界面上按钮背后的那个函数，操作的是同一份状态：用户能看到 agent 做的改动，agent 也能看到用户做的改动。

网站：https://clientmcp.dev/

## 解决什么问题

agent 想操作一个应用，通常只能从外面下手：截图加模拟点击，或者调一个单独的后端 API，但后端看不到应用里当前打开的东西。ClientMCP 让工具直接就是应用里已有的函数，一个动作只实现一次，UI 和 agent 共用，不用截图、不用脚本操作 DOM、也不用模拟输入。

## 怎么工作

```text
应用（Client SDK） ──WebSocket──▶ Bridge ◀──MCP Streamable HTTP── Agent（任何 MCP 客户端）
```

- **应用里不开端口**：应用只发起一条出站 WebSocket 连到 bridge，跑在 NAT 后面的浏览器标签页也能用。
- **Bridge**：在 WebSocket 和 MCP 之间做转换。一份 Rust 核心，两种运行方式：静态 Linux 二进制 / Docker，或者 Cloudflare Workers + Durable Objects。
- **任何 MCP 客户端都能接**：只需要 MCP Streamable HTTP 和一个 bearer token。
- **离线也是一种状态**：应用关了就没有工具；重新打开时 agent 会收到 `tools/list_changed`。
- **耗时调用**：慢的调用走 SSE 并保持连接，用户可以慢慢确认。
- **无状态 token**：HS256 JWT，密钥可以不停机轮换。

## 快速上手

1. 跑一个 bridge：

   ```sh
   git clone https://github.com/atshelchin/clientmcp && cd clientmcp
   docker build -t clientmcp .
   export CLIENTMCP_SECRET=$(openssl rand -hex 32)
   docker run -d -p 8080:8080 -e CLIENTMCP_SECRET clientmcp
   ```

2. 生成 token：

   ```sh
   docker run --rm -e CLIENTMCP_SECRET clientmcp token client my-app
   docker run --rm -e CLIENTMCP_SECRET clientmcp token agent my-app --ttl 30d
   ```

3. 在应用里暴露函数：

   ```js
   import { ClientMCP } from "clientmcp";

   const mcp = new ClientMCP({ url: "ws://localhost:8080/connect", token: CLIENT_TOKEN });
   mcp.expose("add_todo", {
     description: "Add a todo",
     inputSchema: { type: "object", properties: { title: { type: "string" } }, required: ["title"] },
     handler: ({ title }) => todos.add(title), // the same action the UI calls
   });
   await mcp.connect();
   ```

4. 接上 agent（以 Claude Code 为例）：

   ```sh
   claude mcp add --transport http my-app http://localhost:8080/mcp \
     --header "Authorization: Bearer $AGENT_TOKEN"
   ```

JavaScript SDK 没有依赖，支持浏览器、Node.js 22+、Deno、Bun；Rust 应用可以用 `clientmcp-client`。

## 注意

- bridge 是被信任的一方：它终止 TLS，能看到所有参数和结果，agent 和应用之间不是端到端加密。
- v1 只支持 tools，不支持 resources、prompts 和进度通知。
- 参数来自大模型，可能被提示词注入操纵；应用要自己校验参数，重要操作要让用户确认。

## 开源

开放协议 v1.0，MIT 或 Apache-2.0 双协议：[github.com/atshelchin/clientmcp](https://github.com/atshelchin/clientmcp)
