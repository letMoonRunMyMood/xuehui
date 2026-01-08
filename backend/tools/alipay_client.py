# alipay_client.py - 沙箱环境专用
from alipay import AliPay
from alipay_config import AlipayConfig
import logging


class AlipayClient:
    orders={}

    def __init__(self):
        # 沙箱环境配置
        self.client = AliPay(
            appid=AlipayConfig.ALIPAY_APP_ID,
            app_notify_url=AlipayConfig.ALIPAY_NOTIFY_URL,
            app_private_key_string=AlipayConfig.ALIPAY_APP_PRIVATE_KEY,
            alipay_public_key_string=AlipayConfig.ALIPAY_PUBLIC_KEY,
            sign_type="RSA2",
            debug=True  # 沙箱环境建议开启debug
        )

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_sandbox_web_pay(self, order_id, amount, subject, body,return_url=AlipayConfig.ALIPAY_RETURN_URL,notify_url=AlipayConfig.ALIPAY_NOTIFY_URL):
        """
        创建沙箱环境网页支付订单
        """
        try:
            # 沙箱环境订单信息
            order_string = self.client.api_alipay_trade_page_pay(
                out_trade_no=order_id,
                total_amount=str(amount),
                subject=subject,
                body=body,
                return_url=return_url,
                notify_url=notify_url
            )

            # 生成沙箱支付URL
            pay_url = f"{AlipayConfig.ALIPAY_GATEWAY}?{order_string}"

            self.logger.info(f"沙箱支付URL生成成功: {order_id}")
            self.logger.info(f"支付URL: {pay_url}")

            return pay_url

        except Exception as e:
            self.logger.error(f"沙箱支付订单创建失败: {str(e)}")
            return None

    def create_sandbox_mobile_pay(self, order_id, amount, subject, body="沙箱环境手机测试"):
        """
        创建沙箱环境手机支付订单
        """
        try:
            order_string = self.client.api_alipay_trade_wap_pay(
                out_trade_no=order_id,
                total_amount=str(amount),
                subject=subject,
                body=body,
                return_url=AlipayConfig.ALIPAY_RETURN_URL,
                notify_url=AlipayConfig.ALIPAY_NOTIFY_URL
            )

            pay_url = f"{AlipayConfig.ALIPAY_GATEWAY}?{order_string}"

            self.logger.info(f"沙箱手机支付URL生成成功: {order_id}")
            return pay_url

        except Exception as e:
            self.logger.error(f"沙箱手机支付订单创建失败: {str(e)}")
            return None

    def verify_sandbox_notify(self, data):
        """
        验证沙箱环境异步通知
        """
        try:
            # 复制数据用于验证
            verify_data = data.copy()
            signature = verify_data.pop("sign", None)

            if not signature:
                self.logger.error("沙箱通知缺少签名")
                return False

            # 验证签名
            success = self.client.verify(verify_data, signature)

            if success:
                self.logger.info("沙箱通知验证成功")
            else:
                self.logger.error("沙箱通知验证失败")

            return success

        except Exception as e:
            self.logger.error(f"沙箱通知验证异常: {str(e)}")
            return False

    def query_sandbox_order(self, order_id):
        """
        查询沙箱环境订单状态
        """
        try:
            result = self.client.api_alipay_trade_query(out_trade_no=order_id)

            if result.get("code") == "10000":
                self.logger.info(f"沙箱订单查询成功: {order_id}")
                return result
            else:
                self.logger.error(f"沙箱订单查询失败: {result}")
                return None

        except Exception as e:
            self.logger.error(f"沙箱订单查询异常: {str(e)}")
            return None

    def sandbox_refund(self, order_id, refund_amount, reason="沙箱环境测试退款"):
        """
        沙箱环境退款
        """
        try:
            result = self.client.api_alipay_trade_refund(
                out_trade_no=order_id,
                refund_amount=str(refund_amount),
                refund_reason=reason
            )

            if result.get("code") == "10000":
                self.logger.info(f"沙箱退款成功: {order_id}")
                return result
            else:
                self.logger.error(f"沙箱退款失败: {result}")
                return None

        except Exception as e:
            self.logger.error(f"沙箱退款异常: {str(e)}")
            return None

    def get_sandbox_info(self):
        """
        获取沙箱环境信息
        """
        return {
            "gateway": AlipayConfig.ALIPAY_GATEWAY,
            "app_id": AlipayConfig.ALIPAY_APP_ID,
            "accounts": AlipayConfig.SANDBOX_ACCOUNTS,
            "tips": [
                "这是支付宝沙箱环境，用于开发测试",
                "使用沙箱账号进行支付测试",
                "所有交易都是模拟的，不会产生真实资金流转",
                "测试完成后记得切换到正式环境"
            ]
        }