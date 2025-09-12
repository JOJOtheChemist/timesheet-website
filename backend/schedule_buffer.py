import threading
import time
from typing import List, Dict, Any, Optional
from collections import deque

# 简单的内存缓冲 + 批量持久化工作线程
class ScheduleBuffer:
	def __init__(self, flush_interval_seconds: float = 1.0, max_batch_size: int = 200):
		self._queue = deque()  # type: deque[Dict[str, Any]]
		self._lock = threading.Lock()
		self._stop = threading.Event()
		self._flush_interval = flush_interval_seconds
		self._max_batch_size = max_batch_size
		self._worker: Optional[threading.Thread] = None
		self._db_getter = None  # callable to acquire DB connection

	def start(self, db_getter):
		self._db_getter = db_getter
		if self._worker and self._worker.is_alive():
			return
		self._stop.clear()
		self._worker = threading.Thread(target=self._run, name="ScheduleBufferWorker", daemon=True)
		self._worker.start()

	def stop(self):
		self._stop.set()
		if self._worker:
			self._worker.join(timeout=2.0)

	def enqueue(self, item: Dict[str, Any]):
		# item 需要包含: user_id, schedule_date, time_slot, planned_subtask_id, planned_notes, actual_subtask_id, actual_notes, mood
		with self._lock:
			self._queue.append(item)

	def size(self) -> int:
		with self._lock:
			return len(self._queue)

	def flush_once(self):
		batch: List[Dict[str, Any]] = []
		with self._lock:
			while self._queue and len(batch) < self._max_batch_size:
				batch.append(self._queue.popleft())
		if not batch:
			return 0
		# 批量 upsert
		conn = None
		cursor = None
		try:
			conn = self._db_getter()
			cursor = conn.cursor()
			# 使用临时表或多值 INSERT ... ON DUPLICATE KEY UPDATE
			values = []
			for it in batch:
				values.append((
					it.get('user_id'),
					it.get('schedule_date'), it.get('time_slot'),
					it.get('planned_subtask_id'), it.get('planned_notes'),
					it.get('actual_subtask_id'), it.get('actual_notes'), it.get('mood')
				))
			# 分批执行，避免单条 SQL 过大
			chunk = 100
			affected = 0
			for i in range(0, len(values), chunk):
				part = values[i:i+chunk]
				placeholders = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s)"] * len(part))
				sql = f"""
					INSERT INTO daily_schedule (
						user_id, schedule_date, time_slot,
						planned_subtask_id, planned_notes,
						actual_subtask_id, actual_notes, mood
					) VALUES {placeholders}
					ON DUPLICATE KEY UPDATE
						planned_subtask_id=VALUES(planned_subtask_id),
						planned_notes=VALUES(planned_notes),
						actual_subtask_id=VALUES(actual_subtask_id),
						actual_notes=VALUES(actual_notes),
						mood=VALUES(mood),
						updated_at=CURRENT_TIMESTAMP
				"""
				flat = []
				for row in part:
					flat.extend(row)
				cursor.execute(sql, flat)
				affected += cursor.rowcount
			conn.commit()
			return affected
		except Exception:
			# 失败将本批次重新放回队列头，避免数据丢失
			with self._lock:
				for it in reversed(batch):
					self._queue.appendleft(it)
			return 0
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def _run(self):
		while not self._stop.is_set():
			try:
				self.flush_once()
			except Exception:
				pass
			time.sleep(self._flush_interval)

# 单例缓冲器
buffer = ScheduleBuffer(flush_interval_seconds=0.5, max_batch_size=200) 