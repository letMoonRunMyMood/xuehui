from datetime import datetime, timedelta
from typing import Dict, Optional
import threading
import time


class EmailCaptchaMemoryStorage:
    """内存存储验证码的类，带有自动清理功能"""
    _instance = None
    _storage: Dict[str, dict] = {}
    _cleanup_interval = 600  # 清理间隔，单位秒（默认10分钟）
    _cleanup_thread = None
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._start_cleanup_thread()
        return cls._instance

    @classmethod
    def add_captcha(cls, email: str, captcha: str, expires_in: int = 600) -> None:
        """添加验证码到内存存储"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        cls._storage[email] = {
            'captcha': captcha,
            'expires_at': expires_at
        }

    @classmethod
    def get_captcha(cls, email: str) -> Optional[dict]:
        """获取验证码信息"""
        return cls._storage.get(email)

    @classmethod
    def delete_captcha(cls, email: str) -> None:
        """删除验证码"""
        cls._storage.pop(email, None)

    @classmethod
    def is_valid(cls, email: str, captcha: str) -> bool:
        """验证验证码是否正确且未过期"""
        captcha_info = cls.get_captcha(email)
        if not captcha_info:
            return False

        is_correct = captcha_info['captcha'] == captcha
        is_expired = datetime.utcnow() > captcha_info['expires_at']

        return is_correct and not is_expired

    @classmethod
    def _cleanup_expired_captchas(cls):
        """清理过期的验证码"""
        now = datetime.utcnow()
        expired_emails = [
            email for email, captcha_info in cls._storage.items()
            if now > captcha_info['expires_at']
        ]
        for email in expired_emails:
            cls._storage.pop(email, None)
        print(f"清理了 {len(expired_emails)} 个过期验证码")  # 调试用，生产环境可以移除

    @classmethod
    def _cleanup_loop(cls):
        """清理线程的循环"""
        while cls._running:
            cls._cleanup_expired_captchas()
            time.sleep(cls._cleanup_interval)

    @classmethod
    def _start_cleanup_thread(cls):
        """启动清理线程"""
        if cls._cleanup_thread is None:
            cls._running = True
            cls._cleanup_thread = threading.Thread(
                target=cls._cleanup_loop,
                daemon=True  # 设置为守护线程，主程序退出时自动结束
            )
            cls._cleanup_thread.start()

    @classmethod
    def stop_cleanup_thread(cls):
        """停止清理线程（通常在程序退出时调用）"""
        cls._running = False
        if cls._cleanup_thread:
            cls._cleanup_thread.join(timeout=1)
        cls._cleanup_thread = None

    @classmethod
    def set_cleanup_interval(cls, interval: int):
        """设置清理间隔（秒）"""
        cls._cleanup_interval = interval