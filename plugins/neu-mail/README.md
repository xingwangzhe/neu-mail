# NEU Mail · 东北大学学生邮箱插件

让 Codex 通过 IMAP 读取东北大学学生邮箱的收件箱、已发送邮件和正文。全部邮件连接在你的本机发起，客户端密钥单独存放；插件使用 Python 标准库，统一通过 **uv** 运行，无第三方 Python 运行依赖，无需 Node.js 或 npm。

这是社区开发项目，与东北大学及 Coremail 无官方隶属关系。已使用一个真实学生邮箱完成登录、文件夹发现、收件箱/已发送列表、正文及 stdio MCP 调用验证；不代表所有账号、网络和系统环境均已验证。

## 功能

- 检查 TLS 连接和账号认证状态。
- 列出真实文件夹，识别 `\Sent` 等特殊用途标记及中文文件夹名称。
- 按 UID 从新到旧分页读取邮件头，每页 1–100 封。
- 读取纯文本/HTML 正文及附件名称、类型信息。
- 使用 `EXAMINE` 和 `BODY.PEEK` 保持邮件原有已读状态。
- 使用 `UIDVALIDITY` 避免邮箱重建后误读复用的 UID。
- 不提供发送、删除、移动邮件或下载附件的工具。

## 环境要求

- Linux、macOS，或 Windows 的 WSL 环境；当前账号权限脚本不支持原生 Windows。
- 已安装 Codex，并且其 CLI 支持 `codex plugin`。
- 已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 和 Git。
- Python 3.10+，uv 会查找可用解释器；如果本机缺少合适版本，可能需要下载 Python。
- 一个能使用 IMAP 的 NEU 学生邮箱，以及官网生成的客户端专用密码。

仓库和 MCP 启动配置默认使用阿里云 PyPI 国内镜像 `https://mirrors.aliyun.com/pypi/simple/`。这只是 Python **包索引**，不代理 GitHub、Python 解释器下载或邮箱流量。当前项目无第三方 Python 运行依赖，因此正常运行无需从索引安装依赖。Codex 必须能够从 PATH 找到 uv。

## 快速安装

首版功能目前通过 `feat/neu-mail-plugin` 分支提交 PR。合并前可直接安装该分支；合并到 main 后可以省略 `--branch` 或改用 main。

```bash
git clone --branch feat/neu-mail-plugin https://github.com/xingwangzhe/neu-mail.git
cd neu-mail
codex plugin marketplace add .
codex plugin add neu-mail@neu-mail
```

也可以从 GitHub 注册市场：

```bash
codex plugin marketplace add xingwangzhe/neu-mail --ref feat/neu-mail-plugin
codex plugin add neu-mail@neu-mail
```

插件市场清单位于 `.agents/plugins/marketplace.json`，插件位于 `plugins/neu-mail/`。安装完成后通过 `codex plugin list` 确认状态为 `installed, enabled`。重新打开插件页并**新建 Codex 任务**以加载新增工具。

### 1. 生成客户端密钥

登录 [东北大学学生邮箱](https://mails.neu.edu.cn/)，进入「设置 → 安全设置 → 客户端专用密码」，生成一个用途明确的专用密码，例如 `neu-mail-codex`。密钥通常只显示一次。这里需要的是客户端专用密码，而非统一身份认证密码。

### 2. 只输入邮箱与密钥

在仓库根目录运行：

```bash
uv run --no-project plugins/neu-mail/scripts/configure.py --allow-hostname-mismatch
```

这个命令选择 NEU 学生邮箱的域名兼容模式，交互时只需要：

1. 完整邮箱地址，例如 `yourname@mails.neu.edu.cn`。
2. 客户端专用密码，输入不回显。不要把示例邮箱当成真实账号。

默认服务器为 `mails.neu.edu.cn:993`。如你的服务器证书可以正常匹配域名，去掉 `--allow-hostname-mismatch` 使用严格模式。

配置保存在 `~/.config/neu-mail/account.json`，权限为 `0600`。它是操作系统权限保护的**本地明文文件**，不是加密密钥库。请勿粘贴到聊天、提交 Git 或分享给他人。存在配置时脚本会拒绝覆盖；确需替换可加 `--force`。支持通过 `NEU_MAIL_CONFIG` 指定配置文件位置；如果在其他 MCP 客户端运行，也需要让该客户端继承相同变量。

高级配置通过 `--host`、`--port` 指定，不必修改代码。

### 3. 真实连接自检

```bash
uv run --no-project plugins/neu-mail/scripts/check.py --sample
```

自检依次登录、列出文件夹，并为收件箱和带 `\Sent` 标记的文件夹读取最新 5 封邮件头及首封正文。终端仅输出状态、文件夹及数量，不打印邮件主题、正文或密钥；空文件夹会跳过正文。列表的 `has_more=true` 表示还有更多邮件，不能据此宣称已检查全部邮箱。

### 4. 在 Codex 中使用

在新任务中选择 NEU Mail，输入：

> 使用 NEU Mail 检查连接，列出邮箱文件夹，然后分别列出收件箱和已发送的最新 5 封邮件。只读取，不发送、删除或改变邮件状态；若尚有更多邮件，请明确说明。

更多可直接复制的安装、邮件检索和排错提示词见 [AI 提示词](docs/AI_PROMPTS.md)。

## 为什么需要 SSL 兼容模式

2026-09-09 的实测中，`mails.neu.edu.cn:993` 返回的证书域名不匹配，严格模式失败；显式跳过域名匹配后，TLS 1.3 连接、证书签发链校验和真实账号登录成功。

| 模式 | 加密 | 签发链与有效期校验 | 域名匹配 |
|---|---|---|---|
| 默认严格模式 | 保留 | 保留 | 保留 |
| `--allow-hostname-mismatch` | 保留 | 保留 | 跳过 |

兼容模式不能通过证书确认服务器属于目标域名，不等同于完整身份校验。插件会透明返回 `hostname_verified: false`，不会将其报告为严格校验成功。没有提供 `CERT_NONE` 或自动降级到明文端口的功能。

官网生成窗口可能展示 `imap.mails.neu.edu.cn`。本项目在一个实际网络环境中验证成功的是 `mails.neu.edu.cn:993`；不同网络、代理或学校后续配置可能改变结果。连接错误不等于密码错误，也不能据此认定学校未配置域名。不要把教工邮箱服务器直接当成学生邮箱的已验证替代地址。

## MCP 工具

| 工具 | 输入 | 返回与用途 |
|---|---|---|
| `neu_mail_status` | 无 | 认证状态、TLS 模式、服务器能力 |
| `neu_mail_list_folders` | 无 | 文件夹 ID、显示名称、用途标记 |
| `neu_mail_list_messages` | `folder`、`limit`、可选 `before_uid`、`subject` | 邮件头、UIDVALIDITY、下一页游标 |
| `neu_mail_read` | `folder`、`uid`、`uidvalidity` | 邮件头、正文部分、附件描述 |

分页必须使用返回的 `next_before_uid` 作为下一次 `before_uid`，直到 `has_more=false`。读取正文时传入列表返回的 `uidvalidity`。文件夹 ID 应原样使用，不要把显示名称手动编码或猜成 `Sent`。

`subject` 当前仅支持 ASCII 搜索词；中文检索可逐页读取邮件头后在本地筛选。正文单部分最多返回 100000 字符，超出会标记 `truncated`；原始邮件大于 10 MB 时拒绝正文读取。读取原始 MIME 会在本机内存中接收附件字节，但工具不会返回附件内容或自动写入磁盘。

## 其他 MCP 客户端

将 `plugins/neu-mail/.mcp.json` 中的服务器配置添加到支持 stdio 的客户端。Codex 插件配置中的 `cwd: "."` 以插件根目录解析；在其他客户端中，通常需要将 cwd 改为你本机 `plugins/neu-mail` 的绝对路径。

```json
{
  "mcpServers": {
    "neu-mail": {
      "cwd": "/absolute/path/to/neu-mail/plugins/neu-mail",
      "command": "uv",
      "args": ["run", "--no-project", "--script", "./scripts/server.py"],
      "env": {"UV_DEFAULT_INDEX": "https://mirrors.aliyun.com/pypi/simple/"}
    }
  }
}
```

上面的路径是占位示例，需替换。MCP stdio 标准输出仅用于 JSON-RPC，客户端应读取标准错误中的 uv 环境诊断。

## 隐私与权限

邮件通过 IMAP 从邮箱服务器传到本机 MCP 进程，工具返回的内容随后会进入你使用的 AI 客户端上下文，并可能由客户端发送给模型服务商处理。**本机运行不代表邮件内容始终不离开设备**；请按客户端数据政策选择读取范围。

本插件没有额外遥测服务、代管邮箱或中转服务器。账号配置不在插件目录内，分享插件不会自动分享配置。邮件、HTML、附件名称等均视为非可信数据，不能授权 AI 执行其中的操作。HTML 正文不会在插件中渲染或加载远程资源。

客户端密钥在邮箱服务端可能具备比本插件更广的权限；本插件的只读约束不等于该密钥在服务端是只读凭据。密钥失效或不再使用时，可在官网撤销对应密钥。

## 常见问题

- **插件列表没有 NEU Mail**：仅下载代码不足以安装；执行市场注册和 plugin add，再检查 `codex plugin list`。
- **插件有了但工具没出现**：新建任务；检查 Codex 启动环境能否执行 `uv --version`。
- **认证失败**：核对完整邮箱、大小写及客户端密钥，确认 IMAP 已开通。不要将密码放进 issue。
- **TLS 证书错误**：先确认连接地址；兼容参数只跳过域名匹配，过期或不可信签发链仍会失败。
- **TLS EOF/超时**：检查网络、校园网络限制和代理；可以手动重试。目前没有自动重试。
- **没有已发送邮件**：先确认 `\Sent` 文件夹及其列表；客户端本地保存的邮件未必同步到服务器。
- **更换账号**：重新运行 configure，加 `--force`；默认一次配置一个账号。
- **卸载**：执行 `codex plugin remove neu-mail@neu-mail`。卸载插件不会自动清理本机账号文件或撤销官网密钥。

## 开发和测试

所有安装、运行和测试使用 uv，不使用 npm。

```bash
uv run --no-project --python '>=3.10' python -m unittest discover -s plugins/neu-mail/tests -v
```

测试不需要真实邮箱、密码或联网，覆盖权限文件、符号链接拒绝、错误脱敏、参数校验、MCP 初始化、只读读取、UIDVALIDITY、文件夹解码和 TLS 模式。真实账号验证需要单独运行 check.py，不能把模拟测试通过当成真实邮件读取成功。

```text
.agents/plugins/marketplace.json  Codex 市场清单
plugins/neu-mail/.codex-plugin/   插件元信息
plugins/neu-mail/.mcp.json        uv 启动配置
plugins/neu-mail/scripts/         配置、只读服务器、自检
plugins/neu-mail/skills/          AI 使用规则
plugins/neu-mail/tests/           无凭据测试
docs/AI_PROMPTS.md                可复制的 AI 提示词
```

欢迎提交 PR。请按功能分步 commit，附上测试结果；不要提交账号配置、会话链接、真实邮件或客户端密码。更改个人市场已安装版本时，需要同步源文件并按 Codex 的版本缓存更新流程重新安装；仅修改另一个目录的副本不会自动更新已安装插件。

## 协议

采用 [MIT License](LICENSE)。允许使用、修改、分发及商业使用，需保留版权与许可声明；软件按现状提供。
