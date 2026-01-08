from decorator import login_required
from exts import db
from . import course_bp
from flask import request, jsonify, session
from blueprints.models.chapter import ChapterModel

@course_bp.patch('/update-chapter')
@login_required
def update_chapter():
    try:
        # 验证用户权限
        if session.get('role') != 1:
            return jsonify({
                'success': False,
                'message': '用户无权限修改章节！',
                'data': None
            }), 403

        # 获取请求数据
        chapter_id = int(request.form.get('chapter_id'))
        # 验证必填字段
        if not chapter_id:
            return jsonify({
                'success': False,
                'message': '章节ID为必填项！',
                'data': None
            }), 400
        # 检查章节是否存在
        chapter = ChapterModel.query.get(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'message': '指定的章节不存在！',
                'data': None
            }), 404

        if 'title' in request.form and request.form['title'] != chapter.title:
            title = request.form.get('title')
            chapter.title = title

        if 'order' in request.form and request.form['order'] != chapter.order:
            order = int(request.form.get('order'))
            chapter.order = order

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '成功更新章节信息！',
            'data': {
                'id': chapter.id,
                'title': chapter.title,
                'course_id': chapter.course_id,
                'order': chapter.order
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "data": None
        }), 500