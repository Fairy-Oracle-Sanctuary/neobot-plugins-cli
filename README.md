# neobot-plugins-cli

**NeoBot 插件快速原型测试 CLI** —— 轻量 REPL，无需 Redis / MySQL / NapCat 即可加载并触发插件命令。

基于 [NeoBot](https://github.com/Fairy-Oracle-Sanctuary/NeoBot) 的 **plugin-api-v1** 契约，内置该契约的轻量 stub，让插件开发者 clone 下来就能跑、就能测，不需要搭整套框架环境。

## 安装

```bash
pip install neobot-plugins-cli
```

## 快速开始

```bash
# 加载插件目录并进入交互 REPL
neobot-lab path/to/my_plugin

# 单次执行一条命令(适合脚本 / CI)
neobot-lab path/to/my_plugin --once "/echo 你好"

# 指定模拟平台
neobot-lab path/to/my_plugin --platform discord
```

## REPL 用法

```
lab> /help              查看已注册指令
lab> /echo 你好         触发 /echo 指令
lab> 普通消息文本        触发 on_message 处理器
lab> /quit              退出
```

插件中的 `event.reply(...)` 输出会以 `▶` 前缀打印；`bot.call_api(...)` 等调用被记录在 `bot.api_calls` 中。

## 它做了什么

| 能力 | 说明 |
|---|---|
| 契约 stub | 内置 `neobot.plugin_api` 轻量实现：`command` / `platform_command` / `on_message` / `on_notice` / `on_request` / `define_plugin` / `MessageSegment` / `Bot` / `Permission` 等 |
| 命令触发 | 输入 `/命令 参数`，按 handler 签名自动传参（兼容 `(bot, event, args)`、`(bot, event, permission_granted)` 等形态） |
| 回复收集 | `event.reply()` 的回复输出到终端，方便肉眼验证 |
| 内存服务 | `redis_manager` / `permission_manager` / `image_manager` 等为内存占位，不落盘、不联网 |
| 平台模拟 | `--platform qq / discord / cli / mcc`，`platform_command` 按平台路由 |

## 为什么需要它

插件开发最大的痛点：为了测一个命令，要起 NapCat、Redis、MySQL 整套环境。`neobot-lab` 让插件在**纯本地、零依赖**下快速原型验证——先跑通逻辑，再上真实环境联调。

## 限制

- 仅供**原型测试**，不是真实运行环境（无消息收发、无持久化、无真实权限校验）
- 服务单例为内存占位，插件若依赖真实 Redis / 网络请求，需自行 mock 或改用真实框架
- 与真实 NeoBot 框架**不要在同一环境安装**（两者都提供 `neobot.plugin_api` 命名空间）

## 开发

```bash
pip install -e . pytest
pytest tests/
```

## 许可证

**GNU Affero General Public License v3.0 (AGPL-3.0)** — 见 [LICENSE](LICENSE)。
