import json
import os
from dotenv import load_dotenv

# 1. 打印当前工作目录，这是定位路径问题的关键
print(f"[调试信息] 程序当前工作目录: {os.getcwd()}")

load_dotenv()


class AlipayConfig:
    # 沙箱配置
    ALIPAY_APP_ID = os.getenv('ALIPAY_APP_ID', '9021000150614052')

    # 2. 分别获取私钥和公钥的路径，并打印出来
    private_key_path = os.getenv('ALIPAY_APP_PRIVATE_KEY_PATH', 'key/alipay_app_private_key.txt')
    public_key_path = os.getenv('ALIPAY_PUBLIC_KEY_PATH', 'key/alipay_public_key.txt')

    print(f"[调试信息] 将要读取的私钥文件路径: {private_key_path}")
    print(f"[调试信息] 将要读取的公钥文件路径: {public_key_path}")
    
    # 3. 使用打印过的路径变量来打开文件
    try:
        ALIPAY_APP_PRIVATE_KEY = open(private_key_path).read()
        ALIPAY_PUBLIC_KEY = open(public_key_path).read()
    except FileNotFoundError as e:
        print(f"\n[错误] 文件未找到: {e}")
        print("请检查上述打印的路径是否正确，并确保文件存在。")
        # 抛出异常，让程序停止，因为配置文件是必需的
        raise

    ALIPAY_GATEWAY = os.getenv('ALIPAY_GATEWAY', 'https://openapi-sandbox.dl.alipaydev.com/gateway.do')
    ALIPAY_NOTIFY_URL = os.getenv('ALIPAY_NOTIFY_URL', 'http://localhost:5000/pay/pay_notify')
    ALIPAY_RETURN_URL = os.getenv('ALIPAY_RETURN_URL', 'http://localhost:5000/pay/pay_return')

    # 从环境变量读取沙箱账号信息
    @classmethod
    def get_sandbox_accounts(cls):
        """获取沙箱账号配置"""
        return {
            "buyer_email": os.getenv('SANDBOX_BUYER_EMAIL', 'aoqssm4618@sandbox.com'),
            "buyer_password": os.getenv('SANDBOX_BUYER_PASSWORD', '111111'),
            "seller_email": os.getenv('SANDBOX_SELLER_EMAIL', 'mfjmvm7324@sandbox.com'),
            "seller_password": os.getenv('SANDBOX_SELLER_PASSWORD', '111111')
        }

    # 提供类属性访问
    SANDBOX_ACCOUNTS = property(lambda self: self.get_sandbox_accounts())