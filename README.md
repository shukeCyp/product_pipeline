# product_pipeline

郑和数据商品与视频数据采集工具，用于 TikTok 电商选品、类目拉取、商品榜单抓取、关联视频/AI 视频识别和视频下载。

## 功能

- 保存郑和数据登录态
- 抓取商品搜索页筛选项和全量类目树
- 按类目、国家、店铺类型、日期抓取商品列表
- 进入商品详情页抓取关联/对标视频
- 根据 `isAi` 字段筛选 AI 视频
- 通过郑和数据的视频下载接口保存 MP4

## 安装

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

## 使用

先登录一次：

```bash
.venv/bin/python zhenghe.py login
```

抓商品搜索页配置、筛选项和类目：

```bash
.venv/bin/python zhenghe.py inspect
```

抓家居用品某天商品数据：

```bash
.venv/bin/python zhenghe.py products \
  --category-id 600001 \
  --start-date 2026-06-25 \
  --end-date 2026-06-25 \
  --pages 1
```

抓某个商品的关联视频：

```bash
.venv/bin/python zhenghe.py videos \
  --product-id 1733587410864539046 \
  --pages 3
```

下载 AI 视频：

```bash
.venv/bin/python zhenghe.py download-videos \
  --source downloads/product-detail-1733587410864539046/ai-videos.json \
  --limit 5
```

## 输出

```text
.auth/zhenghe-state.json                 # 登录态，本地使用，不提交
downloads/product-search-filters.json    # 商品页筛选项
downloads/categories-tree.json           # 类目树
downloads/categories-flat.json           # 扁平类目
downloads/products-*.json                # 商品数据
downloads/product-detail-*/benchmark-videos.json
downloads/product-detail-*/ai-videos.json
downloads/product-detail-*/videos/*.mp4
```

## 注意

商品和视频接口需要在已登录浏览器上下文里请求。纯后端重放请求可能返回 `查询权限超出`。

不要提交 `.auth/`、`downloads/` 或任何 cookie/token/sign。
