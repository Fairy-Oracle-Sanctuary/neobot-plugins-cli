# neobot-plugins-cli

**NeoBot 插件开发工具链** —— 两个 CLI：

- `neobot-lab`：插件快速原型测试（轻量 REPL，无需 Redis / MySQL / NapCat）
- `neobot-plugin`：插件包管理器（从 Registry 安装 / 更新 / 卸载）

基于 [NeoBot](https://github.com/Fairy-Oracle-Sanctuary/NeoBot) 的 **plugin-api-v1** 契约，内置该契约的轻量 stub，让插件开发者 clone 下来就能跑、就能测，不需要搭整套框架环境。

## 安装

```bash
pip install neobot-plugins-cli
```

---

## 一、neobot-lab —— 原型测试

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

## 二、neobot-plugin —— 包管理器

从官方插件 Registry（[NeoBot-Plugins](https://github.com/Fairy-Oracle-Sanctuary/NeoBot-Plugins) 的 `index.json`）安装插件：

```bash
# 列出 Registry 中的插件
neobot-plugin list

# 搜索插件
neobot-plugin search 图

# 查看插件详情
neobot-plugin info echo

# 安装插件(默认到 ./plugins/,--yes 跳过确认)
neobot-plugin install echo --yes

# 更新插件
neobot-plugin update echo

# 卸载插件
neobot-plugin uninstall echo

# 列出本地已安装
neobot-plugin list --installed
```

**安全设计**：
- 安装前校验每个文件 **SHA256** 与 Registry 索引一致（防篡改）
- 安装时展示插件元信息（描述 / 作者 / 许可 / 依赖 / 文件数）并交互确认
- 生成本地 `manifest.json`，`list --installed` / `update` 依赖它读取版本

支持自定义 Registry 与安装目录：

```bash
neobot-plugin --registry https://example.com/index.json --target ./my_plugins install demo
```

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
