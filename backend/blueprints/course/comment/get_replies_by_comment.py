from flask import jsonify, request
from blueprints.course.comment import comment_bp
from blueprints.models.comment import CommentModel
from blueprints.models.user import UserModel  # 导入用户模型
from decorator import login_required
from exts import db
from sqlalchemy import desc, or_


@comment_bp.get('/<int:parent_comment_id>/get-replies-by-comment')
@login_required
def get_replies_by_comment(parent_comment_id):
    """
    获取指定楼的所有层回复（comment_type=2和3）
    支持多层嵌套回复结构
    """
    try:
        # 验证父评论是否存在
        parent_comment = CommentModel.query.get(parent_comment_id)
        if not parent_comment:
            return jsonify({
                'success': False,
                'message': '未找到该评论',
                'data': None
            }), 404

        # 查询父评论用户信息
        parent_user = UserModel.query.get(parent_comment.user_id)

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        # 根据父评论类型决定查询逻辑
        if parent_comment.comment_type == 1:
            # 如果父评论是楼类型，获取所有层回复（comment_type=2）
            comments_query = CommentModel.query.filter_by(
                parent_id=parent_comment_id,
                comment_type=2
            ).order_by(desc(CommentModel.created_at))
        elif parent_comment.comment_type in [2, 3]:
            # 如果父评论是层类型或回复类型，获取该评论的所有回复（comment_type=3）
            comments_query = CommentModel.query.filter_by(
                parent_id=parent_comment_id,
                comment_type=3
            ).order_by(desc(CommentModel.created_at))
        else:
            return jsonify({
                'success': False,
                'message': '无效的评论类型',
                'data': None
            }), 400

        # 分页
        pagination = comments_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        comments = pagination.items

        # 递归函数：获取评论的所有子回复
        def get_nested_replies(comment_id, depth=0, max_depth=5):
            if depth >= max_depth:
                return []

            # 获取直接子回复
            child_replies = CommentModel.query.filter_by(
                parent_id=comment_id,
                comment_type=3  # 只获取回复类型
            ).order_by(desc(CommentModel.created_at)).all()

            nested_replies = []
            for reply in child_replies:
                # 查询回复用户信息
                reply_user = UserModel.query.get(reply.user_id)
                
                # 获取该回复的子回复（递归）
                child_nested_replies = get_nested_replies(reply.id, depth + 1, max_depth)

                # 计算该回复的总点赞数（包括所有子回复的点赞）
                all_child_ids = [reply.id]
                def collect_child_ids(replies_list):
                    for reply_dict in replies_list:
                        all_child_ids.append(reply_dict['id'])
                        if reply_dict.get('replies'):
                            collect_child_ids(reply_dict['replies'])
                collect_child_ids(child_nested_replies)

                total_likes_query = db.session.query(db.func.sum(CommentModel.likes)).filter(
                    CommentModel.id.in_(all_child_ids)
                ).scalar()

                nested_replies.append({
                    'id': reply.id,
                    'content': reply.content,
                    'image': reply.image,
                    'user_id': reply.user_id,
                    'user_name': reply_user.username if reply_user else '匿名用户',
                    'user_avatar': reply_user.avatar if (reply_user and reply_user.avatar) else '',
                    'user_role': reply_user.role if reply_user else -1,
                    'created_at': reply.created_at.isoformat() if reply.created_at else None,
                    'likes': reply.likes,
                    'total_likes': total_likes_query if total_likes_query else reply.likes,
                    'parent_id': reply.parent_id,
                    'comment_type': reply.comment_type,
                    'reply_count': len(child_nested_replies),
                    'replies': child_nested_replies,
                    'depth': depth
                })

            return nested_replies

        # 格式化返回数据
        replies_data = []
        for comment in comments:
            # 查询回复用户信息
            comment_user = UserModel.query.get(comment.user_id)
            
            # 获取该评论的所有嵌套回复
            nested_replies = get_nested_replies(comment.id)

            # 计算该评论的总点赞数（包括所有嵌套回复的点赞）
            all_reply_ids = [comment.id]
            def collect_all_reply_ids(replies_list, id_list):
                for reply_dict in replies_list:
                    id_list.append(reply_dict['id'])
                    if reply_dict.get('replies'):
                        collect_all_reply_ids(reply_dict['replies'], id_list)
            collect_all_reply_ids(nested_replies, all_reply_ids)

            total_likes_query = db.session.query(db.func.sum(CommentModel.likes)).filter(
                CommentModel.id.in_(all_reply_ids)
            ).scalar()

            reply_data = {
                'id': comment.id,
                'content': comment.content,
                'image': comment.image,
                'user_id': comment.user_id,
                'user_name': comment_user.username if comment_user else '匿名用户',
                'user_avatar': comment_user.avatar if (comment_user and comment_user.avatar) else '',
                'user_role': comment_user.role if comment_user else -1,
                'created_at': comment.created_at.isoformat() if comment.created_at else None,
                'likes': comment.likes,
                'total_likes': total_likes_query if total_likes_query else comment.likes,
                'parent_id': comment.parent_id,
                'comment_type': comment.comment_type,
                'reply_count': len(nested_replies),
                'replies': nested_replies,
                'depth': 0  # 根层深度为0
            }

            # 如果父评论是楼类型，添加楼层信息
            if parent_comment.comment_type == 1:
                # 递归计数所有回复
                def count_all_replies(comment_id):
                    count = 0
                    # 获取所有直接子回复
                    direct_replies = CommentModel.query.filter_by(
                        parent_id=comment_id,
                        comment_type=3
                    ).all()
                    count += len(direct_replies)

                    # 递归计数
                    for reply in direct_replies:
                        count += count_all_replies(reply.id)
                    return count

                total_reply_count = len(nested_replies) + sum(
                    count_all_replies(reply_dict['id']) for reply_dict in nested_replies
                )
                reply_data['total_reply_count'] = total_reply_count
                reply_data['course_id'] = comment.course_id  # 添加课程ID

            replies_data.append(reply_data)

        return jsonify({
            'success': True,
            'message': '获取回复成功',
            'data': {
                'parent_comment': {
                    'id': parent_comment.id,
                    'content': parent_comment.content,
                    'user_id': parent_comment.user_id,
                    'user_name': parent_user.username if parent_user else '匿名用户',
                    'user_avatar': parent_user.avatar if (parent_user and parent_user.avatar) else '',
                    'user_role': parent_user.role if parent_user else -1,
                    'created_at': parent_comment.created_at.isoformat() if parent_comment.created_at else None,
                    'comment_type': parent_comment.comment_type,
                    'parent_id': parent_comment.parent_id,
                    'course_id': parent_comment.course_id,
                    'likes': parent_comment.likes
                },
                'replies': replies_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }), 500