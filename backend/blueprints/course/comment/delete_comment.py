from flask import jsonify, session, request
from sqlalchemy import or_

from blueprints.course.comment import comment_bp
from blueprints.models.comment import CommentModel
from blueprints.models.like import LikeModel
from decorator import login_required
from exts import db


@comment_bp.delete('/delete-comment')
@login_required
def delete_comment():
    """
    删除评论接口
    删除规则：
    1. 管理员可以删除任意评论
    2. 用户只能删除自己的评论
    3. 删除评论时，递归删除所有关联的子评论
    4. 同时删除相关的点赞记录
    """
    try:
        # 获取当前用户ID和角色
        comment_id= request.form.get('comment_id')
        current_user_id = session.get('user_id')
        current_role = session.get('role')

        # 获取目标评论
        comment = CommentModel.query.get(comment_id)
        if not comment:
            return jsonify({
                'success': False,
                'message': '评论不存在！',
                'data': None
            }), 404

        # 权限验证：管理员或评论所有者
        if current_role != 2 and current_user_id != comment.user_id:
            return jsonify({
                'success': False,
                'message': '无权删除该评论！',
                'data': None
            }), 403

        # 递归查找所有需要删除的评论ID（包括当前评论及其所有子评论）
        def find_all_comment_ids(start_id):
            """递归查找所有相关评论ID"""
            all_ids = [start_id]

            # 查找直接子评论
            child_comments = CommentModel.query.filter_by(
                parent_id=start_id
            ).all()

            for child in child_comments:
                # 递归查找子评论的子评论
                all_ids.extend(find_all_comment_ids(child.id))

            return all_ids

        # 获取所有需要删除的评论ID
        all_comment_ids = find_all_comment_ids(comment_id)

        # 删除所有相关评论的点赞记录
        LikeModel.query.filter(
            LikeModel.comment_id.in_(all_comment_ids)
        ).delete(synchronize_session=False)

        # 删除所有相关评论（从叶子节点开始删除，避免外键约束问题）
        # 首先按层级排序：子评论在前，父评论在后
        def get_comment_level(comment_id, level=0):
            """获取评论的层级（0为最顶层）"""
            comment = CommentModel.query.get(comment_id)
            if not comment or comment.parent_id == -1:
                return level
            return get_comment_level(comment.parent_id, level + 1)

        # 按层级从高到低排序（子评论先删除）
        sorted_comment_ids = sorted(
            all_comment_ids,
            key=lambda x: get_comment_level(x),
            reverse=True
        )

        # 批量删除评论
        for cid in sorted_comment_ids:
            comment_to_delete = CommentModel.query.get(cid)
            if comment_to_delete:
                db.session.delete(comment_to_delete)

        db.session.flush()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'评论删除成功！共删除{len(all_comment_ids)}条评论',
            'data': {
                'deleted_comment_id': comment_id,
                'total_deleted': len(all_comment_ids),
                'comment_type': comment.comment_type,
                'course_id': comment.course_id,
                'user_id': comment.user_id
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500