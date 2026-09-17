# HeyPicoo Plugin 接入评估

- 原系统仓库：https://github.com/Nebula-YW/voice-platform-FastAPI
- 系统形态：后端（FastAPI REST + MCP 2 Streamable HTTP）
- Plugin 候选名称：`voice`
- Tool namespace：不适用（首版不发布 Artifact Tool API）
- 接入形态：MCP remote
- 原系统继续拥有：TTS / 语言检测源码、Vercel 部署、Edge TTS 出站调用、REST `/api/v1`
- Plugin Package 包含：`.codex-plugin/plugin.json`、`.mcp.json`、Skill
- Runtime Binding 需要：无凭据公网 HTTPS MCP，endpoint 为 `https://voice-fastapi.nebula-tech.design/mcp`
- Project 物化内容：原生 Agent Plugin（manifest、Skill、MCP 配置）；Agent 把合成的 MP3 写成当前 Project 普通文件
- 身份与凭据边界：匿名公网 MCP，不声明 `bearer_token_env_var`，Package 不内嵌 secret
- 运行时与外部依赖：服务端依赖 Microsoft Edge TTS；语言检测在进程内完成
- 开发与部署环境差异：本地 `http://127.0.0.1:3000/mcp`；HeyPicoo Preview / Production 使用已部署 HTTPS URL。Streamable HTTP 以 `stateless_http=True` 兼容无粘性会话的 serverless 与握手期客户端
- 构建及发布证明：无 CLI binary；Package 发布走 `heypicoo-plugins` 手动 publisher
- 当前状态：转换中
