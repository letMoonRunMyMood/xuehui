from blueprints.course.comment import comment_bp
from flask import request, jsonify
from exts import db
from blueprints.models.comment import CommentModel
from blueprints.models.like import LikeModel
from blueprints.models.user import UserModel
from decorator import login_required

@comment_bp.post('/like-comment')
@login_required
def like_comment():
    """
        点赞或取消点赞评论
        """
    try:
        user_id = int(request.form.get('user_id'))
        comment_id = int(request.form.get('comment_id'))
        is_like = request.form.get('is_like')
        if is_like == 'true':
            is_like = True
        else:
            is_like = False


        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在!',
                'data': None
            }), 404

        comment = CommentModel.query.get(comment_id)
        if not comment:
            return jsonify({
                'success': False,
                'message': '评论不存在!',
                'data': None
            }), 404

        if is_like:
            if LikeModel.query.filter_by(
                comment_id=comment_id,
                user_id=user_id
            ).first():
                return jsonify({
                    'success': False,
                    'message':'点赞已存在！'
                }),409
            like = LikeModel(
                comment_id=comment_id,
                user_id=user_id,
            )
            db.session.add(like)
            comment.likes+=1
        else:
            like = LikeModel.query.filter_by(
                comment_id=comment_id,
                user_id=user_id
            ).first()
            if not like:
                return jsonify({
                    'success': False,
                    'message':'点赞已取消！'
                }),409
            comment.likes-=1
            db.session.delete(like)
        db.session.flush()
        db.session.commit()

        return{
            'success': True,
            'message':'点赞成功!' if is_like else '取消点赞成功！',
            'data': {
                'id':like.id,
                'comment_id':like.comment_id,
                'user_id':like.user_id,
                'created_at':like.created_at,
            }
        }
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500


