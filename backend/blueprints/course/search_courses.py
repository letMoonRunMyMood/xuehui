from decorator import login_required
from exts import db
from . import course_bp
from flask import jsonify, request
from sqlalchemy import func, or_, and_
from datetime import datetime
import random
from blueprints.models.course import CourseModel
from blueprints.models.grade import GradeModel
from blueprints.models.subject import SubjectModel
from blueprints.models.user import UserModel
from blueprints.models.subscribe import SubscribeModel



@course_bp.get('/search-courses')
@login_required
def search_courses():
    """
    课程搜索接口

    查询参数：
    - keyword: 搜索关键字（可选）- 搜索课程名或讲师名
    - grades: 年级ID列表（可选）- 支持多个年级，用逗号分隔
    - subjects: 科目ID列表（可选）- 支持多个科目，用逗号分隔
    - start_date: 开课时间范围开始（可选）- 格式：YYYY-MM-DD
    - end_date: 开课时间范围结束（可选）- 格式：YYYY-MM-DD
    - max_price: 最大订阅价格（可选）- 查询价格小于等于该值的课程
    - sort_mode: 排序模式（必填）- default/subscriber/created_time/price
    - page_size: 页面显示数量（必填）- 每页显示的课程数量
    - page: 当前页数（必填）- 从1开始
    """
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '').strip()
        grades = request.args.get('grades', '').strip()
        subjects = request.args.get('subjects', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        max_price = request.args.get('max_price', '').strip()
        sort_mode = request.args.get('sort_mode', '').strip()
        page_size = request.args.get('page_size', '').strip()
        page = request.args.get('page', '').strip()

        # 参数验证
        if not sort_mode:
            return jsonify({
                'success': False,
                'message': '排序模式不能为空！',
                'data': None
            }), 400

        if sort_mode not in ['default', 'subscriber', 'created_time', 'price']:
            return jsonify({
                'success': False,
                'message': '排序模式必须是：default、subscriber、created_time、price 中的一种！',
                'data': None
            }), 400

        if not page_size or not page_size.isdigit():
            return jsonify({
                'success': False,
                'message': '页面显示数量必须是正整数！',
                'data': None
            }), 400

        if not page or not page.isdigit():
            return jsonify({
                'success': False,
                'message': '当前页数必须是正整数！',
                'data': None
            }), 400

        page_size = int(page_size)
        page = int(page)

        if page_size <= 0 or page <= 0:
            return jsonify({
                'success': False,
                'message': '页面显示数量和当前页数必须大于0！',
                'data': None
            }), 400

        # 价格参数验证
        if max_price:
            try:
                max_price = float(max_price)
                if max_price < 0:
                    return jsonify({
                        'success': False,
                        'message': '最大价格必须大于等于0！',
                        'data': None
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '价格格式错误，必须是数字！',
                    'data': None
                }), 400
        else:
            max_price = None

        # 构建基础查询
        query = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.created_at,
            CourseModel.price,
            CourseModel.grade_id,
            GradeModel.name.label('grade_name'),
            CourseModel.subject_id,
            SubjectModel.name.label('subject_name'),
            CourseModel.teacher_id,
            UserModel.username.label('teacher_name'),
            func.count(SubscribeModel.id).label('subscriber_count')
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).join(
            UserModel, CourseModel.teacher_id == UserModel.id
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
        )

        # 添加搜索条件
        filters = []

        # 关键字搜索（课程名或讲师名）
        if keyword:
            keyword_filter = or_(
                CourseModel.name.contains(keyword),
                UserModel.username.contains(keyword)
            )
            filters.append(keyword_filter)

        # 年级筛选
        if grades:
            try:
                grade_ids = [int(g.strip()) for g in grades.split(',') if g.strip().isdigit()]
                if grade_ids:
                    filters.append(CourseModel.grade_id.in_(grade_ids))
                else:
                    return jsonify({
                        'success': False,
                        'message': '年级ID格式错误！',
                        'data': None
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '年级ID格式错误！',
                    'data': None
                }), 400

        # 科目筛选
        if subjects:
            try:
                subject_ids = [int(s.strip()) for s in subjects.split(',') if s.strip().isdigit()]
                if subject_ids:
                    filters.append(CourseModel.subject_id.in_(subject_ids))
                else:
                    return jsonify({
                        'success': False,
                        'message': '科目ID格式错误！',
                        'data': None
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '科目ID格式错误！',
                    'data': None
                }), 400

        # 开课时间范围筛选
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                filters.append(CourseModel.created_at >= start_dt)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '开始时间格式错误，请使用 YYYY-MM-DD 格式！',
                    'data': None
                }), 400

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                # 结束时间包含当天，所以加一天
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                filters.append(CourseModel.created_at <= end_dt)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '结束时间格式错误，请使用 YYYY-MM-DD 格式！',
                    'data': None
                }), 400

        # 价格筛选
        if max_price is not None:
            filters.append(CourseModel.price <= max_price)

        # 应用所有筛选条件
        if filters:
            query = query.filter(and_(*filters))

        # 分组
        query = query.group_by(CourseModel.id)

        # 排序
        if sort_mode == 'subscriber':
            # 按订阅量排序（高到低）
            query = query.order_by(func.count(SubscribeModel.id).desc(), CourseModel.created_at.desc())
        elif sort_mode == 'created_time':
            # 按开课时间排序（新到旧）
            query = query.order_by(CourseModel.created_at.desc())
        elif sort_mode == 'price':
            # 按价格排序（低到高）
            query = query.order_by(CourseModel.price.asc(), CourseModel.created_at.desc())
        else:  # default
            # 默认排序：获取所有结果后进行混合排序
            pass

        # 获取总数（用于分页信息）
        total_query = query.statement.alias()
        total_count = db.session.query(func.count()).select_from(total_query).scalar()

        # 默认排序的特殊处理
        if sort_mode == 'default':
            # 获取所有结果
            all_courses = query.all()

            # 按订阅量和创建时间分组
            high_subscriber_courses = [c for c in all_courses if c.subscriber_count >= 10]
            new_courses = [c for c in all_courses if (datetime.now() - c.created_at).days <= 30]
            other_courses = [c for c in all_courses if c not in high_subscriber_courses and c not in new_courses]

            # 随机混合排序
            random.shuffle(high_subscriber_courses)
            random.shuffle(new_courses)
            random.shuffle(other_courses)

            # 组合结果：高订阅量课程 + 新课程 + 其他课程
            mixed_courses = high_subscriber_courses + new_courses + other_courses

            # 分页
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            courses = mixed_courses[start_idx:end_idx]
        else:
            # 其他排序模式直接分页
            courses = query.offset((page - 1) * page_size).limit(page_size).all()

        # 构建返回数据
        courses_data = []
        for course in courses:
            cover_url = course.cover
            if cover_url:
                cover_url = cover_url

            courses_data.append({
                'id': course.id,
                'name': course.name,
                'cover': cover_url,
                'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'price': course.price,
                'grade_id': course.grade_id,
                'grade_name': course.grade_name,
                'subject_id': course.subject_id,
                'subject_name': course.subject_name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher_name,
                'subscriber_count': course.subscriber_count
            })

        # 计算分页信息
        total_pages = (total_count + page_size - 1) // page_size

        return jsonify({
            'success': True,
            'message': '成功获取课程列表！',
            'data': {
                'courses': courses_data,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误：{str(e)}',
            'data': None
        }), 500