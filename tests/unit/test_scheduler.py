#!/usr/bin/env python3
"""
智能任务调度系统 - 单元测试套件
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from scheduler.engine import (
    Task, TaskPriority, TaskStatus,
    Worker, IntelligentTaskScheduler
)

class TestTask:
    """任务测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        import datetime
        task = Task(
            priority=TaskPriority.HIGH.value,
            created_at=datetime.datetime.utcnow().timestamp(),
            name='测试任务'
        )
        assert task.task_id is not None
        assert task.name == '测试任务'
        assert task.priority == TaskPriority.HIGH.value
        assert task.status == TaskStatus.PENDING
    
    def test_task_to_dict(self):
        """测试任务序列化"""
        import datetime
        task = Task(
            priority=TaskPriority.NORMAL.value,
            created_at=datetime.datetime.utcnow().timestamp(),
            name='序列化测试'
        )
        data = task.to_dict()
        assert 'task_id' in data
        assert data['name'] == '序列化测试'
        assert data['priority'] == TaskPriority.NORMAL.value

class TestWorker:
    """工作节点测试"""
    
    def test_worker_creation(self):
        """测试工作节点创建"""
        worker = Worker(
            worker_id='worker-1',
            capacity=10
        )
        assert worker.worker_id == 'worker-1'
        assert worker.capacity == 10
        assert worker.current_load == 0
        assert worker.is_available == True
    
    def test_worker_availability(self):
        """测试工作节点可用性"""
        worker = Worker(
            worker_id='worker-1',
            capacity=10,
            current_load=5
        )
        assert worker.available_capacity == 5
        assert worker.is_available == True
        
        worker.current_load = 10
        assert worker.is_available == False

class TestTaskScheduler:
    """调度器测试"""
    
    @pytest.fixture
    def scheduler(self):
        return IntelligentTaskScheduler()
    
    def test_scheduler_initialization(self, scheduler):
        """测试调度器初始化"""
        assert scheduler.task_queue == []
        assert scheduler.workers == {}
    
    def test_submit_task(self, scheduler):
        """测试任务提交"""
        import datetime
        task = Task(
            priority=TaskPriority.HIGH.value,
            created_at=datetime.datetime.utcnow().timestamp(),
            name='测试任务'
        )
        task_id = scheduler.submit_task(task)
        assert task_id is not None
        assert len(scheduler.task_queue) == 1
    
    def test_schedule_next(self, scheduler):
        """测试任务调度"""
        import datetime
        # 注册工作节点
        worker = Worker(
            worker_id='worker-1',
            capacity=10
        )
        scheduler.register_worker(worker)
        
        # 提交任务
        task = Task(
            priority=TaskPriority.HIGH.value,
            created_at=datetime.datetime.utcnow().timestamp(),
            name='调度测试'
        )
        scheduler.submit_task(task)
        
        # 调度任务
        decision = scheduler.schedule_next()
        assert decision is not None
        assert decision['worker_id'] == 'worker-1'
        assert decision['score'] > 0
    
    def test_get_queue_stats(self, scheduler):
        """测试队列统计"""
        stats = scheduler.get_queue_stats()
        assert 'total_tasks' in stats
        assert 'by_priority' in stats
        assert 'total_workers' in stats
        assert 'available_workers' in stats
        assert 'avg_wait_time' in stats
    
    def test_complete_task(self, scheduler):
        """测试任务完成"""
        import datetime
        # 注册工作节点
        worker = Worker(
            worker_id='worker-1',
            capacity=10
        )
        scheduler.register_worker(worker)
        
        # 提交并调度任务
        task = Task(
            priority=TaskPriority.HIGH.value,
            created_at=datetime.datetime.utcnow().timestamp(),
            name='完成测试'
        )
        task_id = scheduler.submit_task(task)
        decision = scheduler.schedule_next()
        
        # 验证任务已调度
        assert decision is not None
        assert decision['task_id'] == task_id
        
        # 完成任务
        result = scheduler.complete_task(task_id, success=True)
        assert result == True

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src/scheduler', '--cov-report=term-missing'])
