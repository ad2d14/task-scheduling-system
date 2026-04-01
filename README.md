# 智能任务调度系统

生产级智能任务调度系统，支持优先级调度、负载均衡、故障恢复。

## 功能特性

- ✅ 任务优先级管理（LOW/NORMAL/HIGH/CRITICAL）
- ✅ 智能调度决策（基于优先级、等待时间、负载、亲和性）
- ✅ 负载均衡（多工作节点）
- ✅ 故障恢复（自动重试）
- ✅ 性能监控（Prometheus + Grafana）
- ✅ 完整测试套件（单元测试 + 集成测试）

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v

# 启动服务
python -m uvicorn src.api.main:app --reload
```

### Docker 部署

```bash
# 构建镜像
docker build -t task-scheduler:latest -f deploy/docker/Dockerfile .

# 运行容器
docker run -p 8000:8000 task-scheduler:latest
```

### K8s 部署

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## 测试覆盖率

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

目标：>80% 覆盖率

## 监控

访问 http://localhost:9090 查看 Prometheus 监控
访问 http://localhost:3000 查看 Grafana 仪表板

## API 文档

启动服务后访问 http://localhost:8000/docs 查看 OpenAPI 文档

## 许可证

MIT License
