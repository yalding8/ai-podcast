# RSSHub 部署与使用指南

## 快速部署

### 1. 启动RSSHub服务

```bash
cd /home/claude/podcast-news-aggregator
docker-compose up -d
```

### 2. 检查服务状态

```bash
docker-compose ps
docker logs podcast-rsshub
```

### 3. 访问RSSHub

浏览器打开: `http://localhost:1200`

---

## 教育类常用RSS路由

### 🏫 教育机构官网

#### IELTS官方
```
https://www.ielts.org/news-and-insights
```

#### TOEFL官方  
```
http://localhost:1200/ets/toefl/news
```

#### British Council
```
http://localhost:1200/britishcouncil/news
```

### 🌍 各国教育部

#### 英国政府教育部
```
https://educationhub.blog.gov.uk/feed/
```

#### 美国教育部
```
http://localhost:1200/ed/gov/news
```

#### 澳大利亚教育部
```
http://localhost:1200/education/gov/au/news
```

### 📰 行业媒体

#### QS世界大学排名新闻
```
http://localhost:1200/topuniversities/news
```

#### Times Higher Education
```
http://localhost:1200/timeshighereducation/news
```

---

## 自定义路由

### 为任意网站创建RSS

如果RSSHub没有预定义路由，可以使用通用路由：

```
http://localhost:1200/rsshub/routes
```

或使用RSS-Bridge作为补充。

---

## 常见问题

### Q1: 如何查看所有可用路由？

访问: `http://localhost:1200`，查看文档

### Q2: RSS更新频率是多少？

默认缓存1小时，可在docker-compose.yml中修改`CACHE_EXPIRE`

### Q3: 如何保护RSSHub不被公开访问？

在docker-compose.yml中设置`ACCESS_KEY`，然后访问时添加:
```
http://localhost:1200/your-route?key=your_secret_key_here
```

### Q4: 服务启动失败怎么办？

```bash
# 查看日志
docker logs podcast-rsshub

# 重启服务
docker-compose restart

# 完全重置
docker-compose down
docker-compose up -d
```

---

## 与其他工具集成

### 集成到Feedly/Inoreader

1. 从RSSHub生成RSS URL
2. 在RSS阅读器中添加订阅
3. 设置更新频率

### 集成到n8n/Make自动化

```javascript
// n8n示例
{
  "nodes": [
    {
      "name": "RSS Feed Read",
      "type": "n8n-nodes-base.rssFeedRead",
      "parameters": {
        "url": "http://localhost:1200/your-route"
      }
    }
  ]
}
```

---

## 性能优化建议

1. **启用Redis缓存** (已在docker-compose中配置)
2. **设置合理的缓存时间** (默认1小时)
3. **使用反向代理** (Nginx/Caddy)
4. **监控日志和性能**

```bash
# 查看Redis缓存统计
docker exec -it podcast-redis redis-cli INFO stats
```

---

## 安全建议

1. ✅ 设置强密码的ACCESS_KEY
2. ✅ 不要暴露在公网（使用内网或VPN）
3. ✅ 定期更新Docker镜像
4. ✅ 监控异常访问日志

```bash
# 更新RSSHub
docker-compose pull
docker-compose up -d
```
