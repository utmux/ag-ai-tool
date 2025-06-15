# AG (AI Gateway) - 你的 Shell AI 助手

![Version 2.0.0](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

`ag` 是一个强大、支持管道的命令行工具，让你可以在终端中无缝地与 GPT 等大型语言模型交互。它的设计遵循 Unix 哲学，可以轻松地集成到你的日常工作流中。

## 简介 (Introduction)

在日常的开发和运维工作中，我们经常需要在终端和 AI 对话之间来回切换。`ag` 旨在打破这种壁垒，将 AI 的能力直接带入 Shell。无论是代码审查、日志分析、还是快速查询，都可以通过简单的管道和命令完成，无需离开你最熟悉的环境。

## 功能特性 (Features)

- **直接提问**：以最自然的方式提问，无需引号，例如 `ag how does https work`。
- **强大的管道支持**：将任何命令的输出通过 `|` 传送给 `ag` 进行处理。
- **交互式对话**：直接运行 `ag` 即可进入持续对话模式，支持上下文记忆。
- **文件内容读取**：使用 `@` 语法，轻松将整个文件内容作为上下文提交，例如 `ag 解释 @main.py 的代码`。
- **多供应商支持**：可配置使用 OpenAI、自定义 API 等多种模型供应商。
- **流式响应**：AI 的回答会以打字机的效果流式输出，无需等待。
- **清晰的职责分离**：使用 `ag` 进行提问，使用独立的 `agc` (ag-config) 命令进行配置管理。

## 架构理念 (Architectural Philosophy)

为了提供最优雅、最无歧义的用户体验，`ag` 采用了双命令分离设计：

| 命令 | 主要职责 | 示例 |
| :--- | :--- | :--- |
| **`ag`** | **核心交互** | `ag what is rust?`, `cat log \| ag analyze`, `ag` (交互模式) |
| **`agc`** | **配置管理** | `agc provider-list`, `agc model-set-default gpt-4o` |

这种设计确保了 `ag` 命令的简洁性，所有管理功能都被整齐地收纳在 `agc` 中。

## 安装与配置 (Installation & Configuration)

#### 1. 克隆项目
```bash
git clone [https://github.com/your-repo/ag-ai-tool.git](https://github.com/utmux/ag-ai-tool.git) # 请替换成您的仓库地址
cd ag-ai-tool
```

#### 2. 安装
建议在 Python 虚拟环境中安装，以避免与系统库冲突。
```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装项目
pip install .

# 在 .bashrc 中添加以下内容：
eval "$(_AG_COMPLETE=bash_source ag)"
eval "$(_AGC_COMPLETE=bash_source agc)"

# 重新加载配置
source ~/.bashrc
```
安装完成后，你将可以在终端中使用 `ag` 和 `agc` 两个命令。

#### 3. 配置 API
`ag` 的所有配置都存放在 `~/.config/ag/config.json` 文件中。首次运行时，程序会自动创建一个默认的配置文件。你需要手动编辑它，填入你的 API 密钥。

**重要提示**: `api_key` 字段应直接填写密钥字符串，**不要**包含 `Bearer ` 前缀。

文件结构示例：
```json
{
    "default_model": "gpt-4o",
    "current_provider": "openai_official",
    "providers": {
        "openai_official": {
            "api_key": "sk-YOUR_OFFICIAL_OPENAI_KEY",
            "api_base": "[https://api.openai.com/v1](https://api.openai.com/v1)",
            "models": ["gpt-4o", "gpt-3.5-turbo"]
        },
        "ctyun_wishub": {
            "api_key": "YOUR_CTYUN_APP_KEY_WITHOUT_BEARER",
            "api_base": "[https://wishub-x1.ctyun.cn/v1](https://wishub-x1.ctyun.cn/v1)",
            "models": ["YOUR_CTYUN_MODEL_ID"],
            "extra_payload": {
                "temperature": 1.0,
                "max_tokens": 4096
            }
        }
    }
}
```
`extra_payload` 是一个可选字段，您可以用它来传递任何额外的请求参数，如 `temperature` 等。

**请务必将 `sk-YOUR_OPENAI_API_KEY` 等占位符替换成您自己的有效密钥。**

## 使用指南 (Usage Guide)

### 核心命令: `ag` (用于提问)

**1. 直接提问 (无需引号)**
```bash
ag what is the capital of France
```

**2. 管道输入**
```bash
# 分析 Nginx 日志中的错误
cat /var/log/nginx/error.log | ag find the root cause of these errors

# 审查代码
cat main.py | ag review this python code for potential bugs
```

**3. 读取文件内容**
```bash
ag explain the logic in @/path/to/your/script.js
```

**4. 交互式对话**
```bash
# 直接运行 ag 即可进入
ag
```
> You: hello
> AG: Hello! How can I assist you today?
> You: tell me a joke
> AG: Why don't scientists trust atoms? Because they make up everything!
> (按 Ctrl+D 结束对话)

**5. 使用特定模型或会话**
```bash
# 使用 gpt-3.5-turbo 模型提问
ag -m gpt-3.5-turbo what is the weather like

# 开始一个全新的会话
ag --new what is our topic today
```

### 配置命令: `agc` (用于管理)

**1. 查看所有供应商**
```bash
agc provider-list
```

**2. 切换默认供应商**
```bash
agc provider-set cephalon_example
```

**3. 设置默认模型**
```bash
agc model-set-default DeepSeek-R1
```
设置后，所有不带 `-m` 参数的 `ag` 命令都会默认使用 `DeepSeek-R1`。

## 结语

我们经历了漫长的调试和重构，最终得到了这个稳定、优雅且功能强大的版本。希望 `ag` 能成为你日常 Shell 操作中的得力助手！
