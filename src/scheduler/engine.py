#!/usr/bin/env python3
"""
智能任务调度系统 - 生产级实现
"""

import heapq
import datetime
import uuid
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(order=True)
class Task:
    """任务数据结构"""
    priority: int
    created_at: float = field(compare=False)
    task_id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    name: str = field(compare=False, default="")
    description: str = field(compare=False, default="")
    payload: Dict[str, Any] = field(compare=False, default_factory=dict)
    status: TaskStatus = field(compare=False, default=TaskStatus.PENDING)
    assigned_worker: Optional[str] = field(compare=False, default=None)
    started_at: Optional[float] = field(compare=False, default=None)
    completed_at: Optional[float] = field(compare=False, default=None)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)
    timeout: int = field(compare=False, default=3600)
    tags: List[str] = field(compare=False, default_factory=list)
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'name': self.name,
            'priority': self.priority,
            'status': self.status.value,
            'created_at': self.created_at,
            'payload': self.payload
        }

@dataclass
class Worker:
    """工作节点"""
    worker_id: str
    capacity: int
    current_load: int = 0
    status: str = "idle"
    tasks: List[str] = field(default_factory=list)
    last_heartbeat: float = field(default_factory=lambda: datetime.datetime.utcnow().timestamp())
    metrics: Dict[str, float] = field(default_factory=dict)
    
    @property
    def available_capacity(self) -> int:
        return self.capacity - self.current_load
    
    @property
    def is_available(self) -> bool:
        return self.status == "idle" and self.available_capacity > 0
    
    def to_dict(self) -> Dict:
        return {
            'worker_id': self.worker_id,
            'capacity': self.capacity,
            'current_load': self.current_load,
            'status': self.status,
            'available_capacity': self.available_capacity
        }

class IntelligentTaskScheduler:
    """
    智能任务调度器 - 生产级实现
    
    功能：
    1. 任务优先级管理
    2. 智能调度决策
    3. 负载均衡
    4. 故障恢复
    5. 性能监控
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.task_queue: List[Task] = []
        self.workers: Dict[str, Worker] = {}
        self.task_history: List[Dict] = []
        self.scheduling_metrics: Dict[str, float] = defaultdict(float)
        
        # 调度策略权重
        self.weights = self.config.get('weights', {
            'priority': 0.4,
            'wait_time': 0.3,
            'worker_load': 0.2,
            'affinity': 0.1
        })
        
        logger.info("调度器初始化完成")
    
    def submit_task(self, task: Task) -> str:
        """提交任务"""
        task.created_at = datetime.datetime.utcnow().timestamp()
        heapq.heappush(self.task_queue, task)
        
        self._record_event('task_submitted', task.task_id, {
            'priority': task.priority,
            'name': task.name
        })
        
        logger.info(f"任务提交：{task.task_id}")
        return task.task_id
    
    def schedule_next(self) -> Optional[Dict]:
        """调度下一个任务"""
        if not self.task_queue:
            return None
        
        task = heapq.heappop(self.task_queue)
        worker = self._select_best_worker(task)
        
        if not worker:
            heapq.heappush(self.task_queue, task)
            return None
        
        score = self._calculate_score(task, worker)
        reasons = self._get_scheduling_reasons(task, worker)
        
        decision = {
            'task_id': task.task_id,
            'worker_id': worker.worker_id,
            'score': score,
            'reasons': reasons,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
        self._assign_task(task, worker)
        
        self._record_event('task_scheduled', task.task_id, decision)
        
        logger.info(f"任务调度：{task.task_id} → {worker.worker_id}")
        return decision
    
    def _select_best_worker(self, task: Task) -> Optional[Worker]:
        """选择最佳工作节点"""
        available_workers = [w for w in self.workers.values() if w.is_available]
        
        if not available_workers:
            return None
        
        worker_scores = []
        for worker in available_workers:
            score = self._calculate_score(task, worker)
            worker_scores.append((score, worker))
        
        if worker_scores:
            best_score, best_worker = max(worker_scores, key=lambda x: x[0])
            return best_worker
        
        return None
    
    def _calculate_score(self, task: Task, worker: Worker) -> float:
        """计算调度分数"""
        score = 0.0
        
        priority_score = task.priority / TaskPriority.CRITICAL.value
        score += self.weights['priority'] * priority_score
        
        wait_time = datetime.datetime.utcnow().timestamp() - task.created_at
        wait_score = min(wait_time / 300, 1.0)
        score += self.weights['wait_time'] * wait_score
        
        load_score = worker.available_capacity / worker.capacity
        score += self.weights['worker_load'] * load_score
        
        affinity_score = self._calculate_affinity(task, worker)
        score += self.weights['affinity'] * affinity_score
        
        return score
    
    def _calculate_affinity(self, task: Task, worker: Worker) -> float:
        """计算亲和性"""
        task_tags = set(task.tags)
        worker_tags = set(worker.metrics.get('tags', []))
        
        if task_tags and worker_tags:
            intersection = len(task_tags & worker_tags)
            union = len(task_tags | worker_tags)
            return intersection / union if union > 0 else 0.0
        
        return 0.5
    
    def _get_scheduling_reasons(self, task: Task, worker: Worker) -> List[str]:
        """获取调度原因"""
        reasons = []
        
        reasons.append(f"任务优先级：{TaskPriority(task.priority).name}")
        reasons.append(f"工作节点负载：{worker.current_load}/{worker.capacity}")
        
        wait_time = datetime.datetime.utcnow().timestamp() - task.created_at
        reasons.append(f"等待时间：{wait_time:.1f}秒")
        
        affinity = self._calculate_affinity(task, worker)
        if affinity > 0.7:
            reasons.append(f"高亲和性：{affinity:.2f}")
        
        return reasons
    
    def _assign_task(self, task: Task, worker: Worker):
        """分配任务"""
        task.status = TaskStatus.RUNNING
        task.assigned_worker = worker.worker_id
        task.started_at = datetime.datetime.utcnow().timestamp()
        
        worker.tasks.append(task.task_id)
        worker.current_load += 1
        if worker.current_load >= worker.capacity:
            worker.status = "busy"
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """完成任务"""
        for worker in self.workers.values():
            if task_id in worker.tasks:
                # 在已分配的任务中查找
                task = None
                for t in self.task_history:
                    if t.get('task_id') == task_id:
                        task = t
                        break
                
                if not task:
                    # 创建任务记录
                    task = {
                        'task_id': task_id,
                        'status': TaskStatus.COMPLETED if success else TaskStatus.FAILED,
                        'completed_at': datetime.datetime.utcnow().timestamp()
                    }
                    self.task_history.append(task)
                else:
                    task['status'] = TaskStatus.COMPLETED.value if success else TaskStatus.FAILED.value
                    task['completed_at'] = datetime.datetime.utcnow().timestamp()
                
                worker.tasks.remove(task_id)
                worker.current_load = max(0, worker.current_load - 1)
                worker.status = "idle"
                
                self._record_event('task_completed', task_id, {
                    'success': success
                })
                
                logger.info(f"任务完成：{task_id}, 成功={success}")
                return True
        return False
    
    def _find_task(self, task_id: str) -> Optional[Task]:
        """查找任务"""
        for task in self.task_queue:
            if task.task_id == task_id:
                return task
        return None
    
    def register_worker(self, worker: Worker) -> str:
        """注册工作节点"""
        self.workers[worker.worker_id] = worker
        self._record_event('worker_registered', worker.worker_id, {
            'capacity': worker.capacity
        })
        logger.info(f"工作节点注册：{worker.worker_id}")
        return worker.worker_id
    
    def heartbeat(self, worker_id: str, metrics: Dict[str, Any]) -> bool:
        """工作节点心跳"""
        if worker_id not in self.workers:
            return False
        
        worker = self.workers[worker_id]
        worker.last_heartbeat = datetime.datetime.utcnow().timestamp()
        worker.metrics.update(metrics)
        
        return True
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计"""
        priority_counts = defaultdict(int)
        for task in self.task_queue:
            priority_counts[TaskPriority(task.priority).name] += 1
        
        return {
            'total_tasks': len(self.task_queue),
            'by_priority': dict(priority_counts),
            'total_workers': len(self.workers),
            'available_workers': sum(1 for w in self.workers.values() if w.is_available),
            'avg_wait_time': self._calculate_avg_wait_time()
        }
    
    def _calculate_avg_wait_time(self) -> float:
        """计算平均等待时间"""
        if not self.task_queue:
            return 0.0
        
        now = datetime.datetime.utcnow().timestamp()
        total_wait = sum(now - task.created_at for task in self.task_queue)
        return total_wait / len(self.task_queue)
    
    def _record_event(self, event_type: str, task_id: str, details: Dict):
        """记录事件"""
        event = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'event_type': event_type,
            'task_id': task_id,
            'details': details
        }
        self.task_history.append(event)
    
    def get_task_history(self, task_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """获取任务历史"""
        history = self.task_history
        if task_id:
            history = [e for e in history if e['task_id'] == task_id]
        return history[-limit:]


if __name__ == '__main__':
    # 示例使用
    config = {
        'weights': {
            'priority': 0.4,
            'wait_time': 0.3,
            'worker_load': 0.2,
            'affinity': 0.1
        }
    }
    scheduler = IntelligentTaskScheduler(config)
    
    # 注册工作节点
    worker1 = Worker(
        worker_id='worker-1',
        capacity=10,
        current_load=0,
        metrics={'tags': ['cpu-intensive', 'gpu']}
    )
    scheduler.register_worker(worker1)
    
    # 提交任务
    task1 = Task(
        priority=TaskPriority.HIGH.value,
        name='数据处理任务',
        description='处理大量数据',
        tags=['cpu-intensive'],
        payload={'data_size': 1000}
    )
    task_id = scheduler.submit_task(task1)
    print(f"任务提交：{task_id}")
    
    # 调度任务
    decision = scheduler.schedule_next()
    if decision:
        print(f"调度决策：任务{decision['task_id']} → 节点{decision['worker_id']}")
        print(f"分数：{decision['score']:.2f}, 原因：{decision['reasons']}")
    
    # 获取统计
    stats = scheduler.get_queue_stats()
    print(f"队列统计：{json.dumps(stats, indent=2)}")
