from decorator import login_required
from . import course_bp
from flask import request, jsonify
from blueprints.models.document import DocumentModel


@course_bp.get('/get-document')
@login_required
def get_document():
    """获取文档详情接口

    接收document_id参数，返回文档的详细信息及可访问的下载路径。
    """
    try:
        # 1. 获取并验证输入参数
        document_id = int(request.args.get('document_id'))
        if not document_id:
            return jsonify({
                'success': False,
                'message': '缺少document_id参数！',
                'data': None
            }), 400

        document_id = int(document_id)

        # 2. 查询文档基本信息
        document = DocumentModel.query.get(document_id)

        if not document:
            return jsonify({
                'success': False,
                'message': '文档不存在！',
                'data': None
            }), 404

        # 3. 处理文档文件路径，生成可访问的URL
        document_url = document.file

        # 4. 构建返回数据 (在视频接口的基础上，增加了title字段，更利于前端展示)
        document_data = {
            'id': document.id,
            'title': document.title,
            'url': document_url,
        }

        # 5. 返回成功响应
        return jsonify({
            'success': True,
            'message': '成功获取文档信息！',
            'data': document_data
        }), 200

    except ValueError:
        return jsonify({
            'success': False,
            'message': 'document_id参数格式错误，应为整数！',
            'data': None
        }), 400
    except Exception as e:
        # 捕获其他所有异常
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500