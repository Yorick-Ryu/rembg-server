# Rembg 背景移除服务器

本项目是一个基于 FastAPI 构建的轻量级 Web 服务器，它封装了强大的 [rembg](https://github.com/danielgatis/rembg) 库，让您可以通过简单的 API 调用来移除图像背景。

经测试，本服务在 **2 核 CPU 和 2GB 内存** 的服务器上即可流畅运行。

我们还开发了一款配套的浏览器插件 [Banana Peel](https://github.com/Yorick-Ryu/BananaPeel)，让您可以直接在网页上右键点击图片移除背景，欢迎体验。

[English](./README.md)

## 使用指南

### 第一步：安装与运行

您可以通过以下两种方式安装并运行本服务。

#### 方法一：本地运行

1.  将此代码仓库克隆到您的本地计算机：
    ```bash
    git clone https://github.com/Yorick-Ryu/rembg-server.git
    cd rembg-server
    ```
2.  安装所需的依赖库：
    ```bash
    pip install rembg[cpu,cli]
    ```
3.  启动服务：
    ```bash
    python main.py
    ```
    服务将默认在 `7001` 端口启动。

#### 方法二：使用 Docker 部署

1.  从 `ghcr.io` 拉取预构建的 Docker 镜像：
    ```bash
    docker pull ghcr.io/yorick-ryu/rembg-server:latest
    ```

2.  运行 Docker 容器：
    ```bash
    docker run -d --name rembg-service -p 7001:7001 ghcr.io/yorick-ryu/rembg-server:latest
    ```

    如果您需要使用自定义端口（例如 `8080`），可以这样运行：
    ```bash
    docker run -d -p 8080:8080 -e PORT=8080 --name rembg-service ghcr.io/yorick-ryu/rembg-server:latest
    ```

### 第二步：配置模型

服务通过 `models.json` 文件来管理和配置可用的 AI 模型。

- **models**: 一个包含多个模型配置的数组。每个配置都包含模型的 `name`（名称）、`desc`（描述）和 `enabled`（是否启用）字段。
- **default_model**: 当 API 请求未指定模型时，将使用此默认模型。

`models.json` 示例：
```json
{
  "models": [
    {
      "name": "u2net",
      "desc": "通用模型",
      "enabled": false
    },
    {
      "name": "silueta",
      "desc": "轻量级通用模型",
      "enabled": true
    },
    {
      "name": "isnet-general-use",
      "desc": "通用模型",
      "enabled": true
    },
    {
      "name": "isnet-anime",
      "desc": "动漫专用模型",
      "enabled": true
    }
  ],
  "default_model": "silueta"
}
```
**注意**：只有 `enabled` 设置为 `true` 的模型才会被加载并可以通过 API 使用。

### 第三步：配合浏览器插件使用

为了更方便地使用，您可以配合我们的浏览器插件 [Banana Peel](https://github.com/Yorick-Ryu/BananaPeel) 一起使用。

1.  访问 [Banana Peel](https://github.com/Yorick-Ryu/BananaPeel) 项目页面，根据说明安装插件。
2.  安装后，点击浏览器右上角的插件图标，在设置中填入您的服务器地址（例如 `http://127.0.0.1:7001`）。

配置完成后，您就可以在任意网页上通过右键菜单快速移除图片背景了。

## API 文档

服务启动后，您可以通过访问 `/docs` 或 `/redoc` 路径来查看由 FastAPI 自动生成的交互式 API 文档。

### GET /

此接口用于检查服务是否正常运行，会返回一条欢迎信息。

- **方法**: `GET`
- **URL**: `/`

#### 响应示例

```json
{
  "message": "欢迎使用 rembg 背景移除服务器。"
}
```

### GET /models

获取当前所有已启用的模型列表。

- **方法**: `GET`
- **URL**: `/models`

#### 使用 cURL 请求示例

```bash
curl http://your-server-ip:7001/models
```

#### 响应示例

```json
{
  "models": [
    {
      "name": "silueta",
      "desc": "轻量级通用"
    },
    {
      "name": "isnet-general-use",
      "desc": "通用"
    },
    {
      "name": "isnet-anime",
      "desc": "动漫"
    }
  ]
}
```

#### 可用模型列表

本项目支持 `rembg` 库中的所有模型（超过15种），以满足不同场景的需求。要查看完整的模型列表、功能描述和效果对比，请访问 `rembg` 官方文档：

**📋 [查看所有可用模型](https://github.com/danielgatis/rembg?tab=readme-ov-file#models)**

以下是一些常用模型：
- `u2net` - 通用的背景移除模型。
- `silueta` - 轻量级模型，处理速度快（仅43MB）。
- `isnet-anime` - 针对动漫和卡通风格图片优化的高精度模型。
- `birefnet-portrait` - 专为人像分割设计的模型。
- `sam` - 功能强大的高级模型，适用于各种复杂场景。

### POST /remove

这是核心的背景移除接口。

- **方法**: `POST`
- **URL**: `/remove`
- **Content-Type**: `multipart/form-data`
- **表单数据**:
  - `file`: 需要处理的图片文件（必需）。
  - `model`: 用于处理的模型名称（可选，默认为 `default_model` 中配置的模型）。该模型必须在 `models.json` 中已启用。

#### 请求参数

| 参数 | 类型 | 是否必需 | 默认值 | 描述 |
|-----------|------|----------|---------|-------------|
| `file` | File | 是 | - | 图片文件（如 JPG, PNG, WebP 等） |
| `model` | String | 否 | `silueta` | 用于背景移除的模型名称 |

#### 响应

- **成功**: 返回处理后的 PNG 格式图片。
- **失败**: 返回包含错误信息的 JSON 数据。

#### 使用 cURL 请求示例

**1. 使用默认模型 (`silueta`):**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  http://your-server-ip:7001/remove \
  -o output.png
```

**2. 指定 `isnet-anime` 模型处理动漫图片:**

```bash
curl -X POST \
  -F "file=@/path/to/your/anime-image.jpg" \
  -F "model=isnet-anime" \
  http://your-server-ip:7001/remove \
  -o output_anime.png
```

**3. 使用 `isnet-general-use` 模型处理通用图片:**

```bash
curl -X POST \
  -F "file=@/path/to/your/image.jpg" \
  -F "model=isnet-general-use" \
  http://your-server-ip:7001/remove \
  -o output_general.png
```

#### 错误响应示例

如果请求了无效或未启用的模型，服务器会返回类似以下的错误：

```json
{
  "detail": "模型 'invalid-model' 不可用或未启用。可用模型: ['silueta', 'isnet-general-use', 'isnet-anime']"
}
```

## 致谢

本项目基于 [@danielgatis](https://github.com/danielgatis) 创建的出色项目 [rembg](https://github.com/danielgatis/rembg) 构建。我们衷心感谢 `rembg` 的作者和所有贡献者，他们让强大的 AI 图像处理技术变得触手可及。

**🙏 特别感谢:**
- [danielgatis/rembg](https://github.com/danielgatis/rembg) - 核心背景移除库。
- `rembg` 社区和所有贡献者。
- 所有为本项目提供支持的 AI 模型（如 U²-Net, IS-Net, BiRefNet, SAM 等）的研究人员。
