---
title: "域名迁移完全指南：从阿里云到 Cloudflare"
description: "详细记录如何将域名从阿里云迁移到 Cloudflare，包括 Pages 部署和自定义域名配置"
slug: domain-migration-aliyun-to-cloudflare
date: 2026-02-17T15:30:00+08:00
lastmod: 2026-02-17T15:30:00+08:00
featured: true
draft: false
categories:
  - DevOps
tags:
  - cloudflare
  - aliyun
  - domain
  - dns
  - migration
  - hugo
  - deployment
---

## 概述

将域名从阿里云迁移到 Cloudflare 是一个提升网站性能和安全性的好选择。本文详细记录完整的迁移流程，包括：

- 域名添加到 Cloudflare
- Hugo 博客部署到 Cloudflare Pages
- 自定义域名配置
- DNS 记录迁移

<!--more-->

## 为什么要迁移到 Cloudflare？

| 特性 | 阿里云 | Cloudflare |
|------|--------|------------|
| CDN | 国内节点快 | 全球节点快 |
| SSL | 部分收费 | 免费 |
| DDoS 防护 | 基础 | 企业级免费 |
| Pages 托管 | 无 | 免费 |
| 开发者生态 | 一般 | 丰富 |

## 迁移流程概览

```
阿里云域名控制台
    ↓
Cloudflare 添加域名
    ↓
Cloudflare Pages 部署
    ↓
配置自定义域名
    ↓
修改阿里云 NS 服务器
    ↓
完成迁移 ✅
```

## 第一步：在 Cloudflare 添加域名

### 方法 1：网页控制台（推荐）

1. 访问 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击 **"Add a site"**
3. 输入域名：`yourdomain.com`
4. 选择 **Free** 计划

### 方法 2：API 方式

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -d '{
    "name": "yourdomain.com",
    "jump_start": true
  }'
```

## 第二步：部署 Hugo 博客到 Cloudflare Pages

### 2.1 准备 GitHub 仓库

```bash
cd your-blog-directory

# 配置 Git 代理（如使用 v2ray/clash）
git config --global http.proxy socks5://127.0.0.1:10808
git config --global https.proxy socks5://127.0.0.1:10808

# 推送代码
git add .
git commit -m "Initial commit"
git push origin main
```

### 2.2 创建 Pages 项目

```bash
# 使用 wrangler CLI
wrangler pages project create your-blog --production-branch=main
```

### 2.3 部署

```bash
# 构建 Hugo 站点
hugo --gc --minify

# 部署到 Pages
wrangler pages deploy public --project-name=your-blog --branch=main
```

部署成功后，你会获得一个 `*.pages.dev` 的预览地址。

## 第三步：添加自定义域名到 Pages

### 3.1 使用 API 添加域名

```bash
ACCOUNT_ID="your-account-id"
TOKEN="your-cloudflare-token"

# 添加根域名
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/your-blog/domains" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"name": "yourdomain.com"}'

# 添加 www 子域名
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/your-blog/domains" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"name": "www.yourdomain.com"}'
```

## 第四步：配置 DNS 记录

### 4.1 删除旧记录

```bash
# 获取现有记录
curl "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY"

# 删除不需要的记录
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/RECORD_ID" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY"
```

### 4.2 添加 CNAME 记录

```bash
# 根域名 → Pages
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "X-Auth-Email: $CF_EMAIL" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -d '{
    "type": "CNAME",
    "name": "@",
    "content": "your-blog.pages.dev",
    "ttl": 1,
    "proxied": true
  }'
```

> **重要**：`proxied: true` 开启 Cloudflare 代理，获得 CDN 加速和 SSL。

## 第五步：修改阿里云 NS 服务器

1. 登录 [阿里云域名控制台](https://dc.console.aliyun.com/)
2. 找到你的域名，点击 **"管理"**
3. 进入 **"DNS 修改"** 或 **"DNS 服务器"**
4. 删除原有的阿里云 NS 地址
5. 填入 Cloudflare 提供的 NS 地址：
   - `xxx.ns.cloudflare.com`
   - `yyy.ns.cloudflare.com`
6. 保存

## 第六步：验证迁移

### 检查 NS 记录

```bash
dig @8.8.8.8 yourdomain.com NS
```

应该返回 Cloudflare 的 NS 服务器。

### 检查网站访问

```bash
curl -I https://yourdomain.com
```

应该返回 `200 OK` 和 Cloudflare 的响应头。

## 完整自动化脚本

```bash
#!/bin/bash
# domain-migration.sh

set -e

# 配置
CF_EMAIL="your@email.com"
CF_API_KEY="your-global-api-key"
ZONE_ID="your-zone-id"
ACCOUNT_ID="your-account-id"
DOMAIN="yourdomain.com"
PROJECT_NAME="your-blog"

echo "🚀 开始域名迁移..."

# 1. 添加域名到 Pages
echo "📦 添加域名到 Pages..."
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/${PROJECT_NAME}/domains" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "{\"name\": \"${DOMAIN}\"}"

# 2. 添加 DNS CNAME
echo "📝 添加 DNS 记录..."
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "X-Auth-Email: ${CF_EMAIL}" \
  -H "X-Auth-Key: ${CF_API_KEY}" \
  -d '{
    "type": "CNAME",
    "name": "@",
    "content": "'${PROJECT_NAME}'.pages.dev",
    "ttl": 1,
    "proxied": true
  }'

echo "✅ 域名配置完成！"
echo "⏳ 请前往阿里云修改 NS 服务器"
echo "🌎 预计 5-30 分钟后生效"
```

## 常见问题

### Q: API 返回 "Authentication error"

**A**: 使用正确的认证方式：
- DNS 操作需要 **Global API Key**（X-Auth-Email + X-Auth-Key）
- Pages 操作可以使用 **API Token**（Authorization: Bearer）

### Q: 域名无法访问

**A**: 检查：
1. NS 服务器是否已修改为 Cloudflare
2. DNS 记录是否正确（CNAME 指向 pages.dev）
3. Pages 项目是否已部署成功

### Q: SSL 证书未颁发

**A**: 
- 确保 `proxied: true` 已开启
- 等待 1-5 分钟
- 检查 Cloudflare SSL/TLS 设置

## 迁移后效果

| 指标 | 迁移前 | 迁移后 |
|------|--------|--------|
| 全球访问速度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| SSL 证书 | 手动配置 | 自动颁发 |
| DDoS 防护 | 基础 | 企业级 |
| 部署流程 | 手动上传 | Git 自动部署 |

## 参考链接

- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Cloudflare API 文档](https://developers.cloudflare.com/api/)
- [Hugo 官方文档](https://gohugo.io/documentation/)

---

*Published on February 17, 2026*
