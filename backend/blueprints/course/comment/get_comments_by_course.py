from flask import jsonify, request
from blueprints.course.comment import comment_bp
from blueprints.models.comment import CommentModel
from blueprints.models.course import CourseModel
from blueprints.models.user import UserModel  # 导入用户模型
from decorator import login_required
from exts import db
from sqlalchemy import desc


@comment_bp.get('/<int:course_id>/get-comments-by-course')
@login_required
def get_comments_by_course(course_id):
    """
    获取指定课程的所有楼回复（comment_type=1）
    """
    try:
        # 验证课程是否存在
        course = CourseModel.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': '未找到该课程',
                'data': None
            }), 404

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 查询comment_type=1的评论（楼回复）
        comments_query = CommentModel.query.filter_by(
            course_id=course_id,
            comment_type=1
        ).order_by(desc(CommentModel.created_at))

        # 分页
        pagination = comments_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        comments = pagination.items

        # 格式化返回数据
        comments_data = []
        for comment in comments:
            # 查询用户基础信息
            user = UserModel.query.get(comment.user_id)
            
            # 计算该楼的点赞总数（包括所有层的点赞）
            total_likes_query = db.session.query(db.func.sum(CommentModel.likes)).filter(
                db.or_(
                    CommentModel.id == comment.id,  # 楼本身的点赞
                    CommentModel.parent_id == comment.id  # 所有子评论的点赞
                )
            ).scalar()

            # 查询该楼的总回复数（包括所有层和对层的回复）
            reply_count = CommentModel.query.filter(
                db.or_(
                    CommentModel.parent_id == comment.id,  # 直接子评论（层）
                    CommentModel.parent_id.in_(
                        db.session.query(CommentModel.id).filter_by(
                            parent_id=comment.id,
                            comment_type=2
                        )  # 层的回复
                    )
                )
            ).count()

            comments_data.append({
                'comment_id': comment.id,
                'content': comment.content,
                'image': comment.image,
                'user_id': comment.user_id,
                'user_name': user.username if user else '匿名用户',  # 用户名
                'user_avatar': user.avatar if (user and user.avatar) else '',  # 头像
                'user_role': user.role if user else -1,  # 角色（0=学生/1=教师/2=管理员）
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': comment.likes,
                'total_likes': total_likes_query if total_likes_query else comment.likes,
                'reply_count': reply_count,
                'parent_id': comment.parent_id,
                'comment_type': comment.comment_type
            })

        return jsonify({
            'success': True,
            'message': '获取评论成功',
            'data': {
                'comments': comments_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500