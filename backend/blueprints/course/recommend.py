from decorator import login_required
from exts import db
from . import course_bp
from flask import jsonify, session
from sqlalchemy import func
from blueprints.models.course import CourseModel
from blueprints.models.grade import GradeModel
from blueprints.models.subject import SubjectModel
from blueprints.models.user import UserModel
from blueprints.models.subscribe import SubscribeModel
import random

from ..models.student_information import StudentInformationModel


@course_bp.get('/recommend')
@login_required
def recommend_courses():
    print('开始处理课程推荐请求')

    try:
        # 获取当前登录用户ID和角色
        user_id = session.get('user_id')
        user_role = session.get('role')

        print(f'从session获取用户信息: user_id={user_id}, role={user_role}')

        if not user_id or user_role is None:
            return jsonify({
                'success': False,
                'message': '用户未登录',
                'data': None
            }), 401

        user_grade = None

        # 只有学生用户（role=0）才有年级信息
        if user_role == 0:
            print('当前用户是学生，尝试获取年级信息')
            # 获取学生信息
            current_student = UserModel.query.get(user_id)
            if not current_student:
                return jsonify({
                    'success': False,
                    'message': '学生用户不存在',
                    'data': None
                }), 404

            current_student_information = StudentInformationModel.query.filter_by(student_id=current_student.id).first()

            # 新增：打印学生对象的详细信息
            print(
                f'学生对象信息: id={current_student.id}, username={current_student.username}, grade={current_student_information.grade}')

            user_grade = current_student_information.grade
            print(f'学生年级信息: grade={user_grade}')
        else:
            print('当前用户不是学生，跳过年级信息获取')
        # 其他类型用户（如教师role=1）没有年级信息，user_grade保持为None

        # 查询课程池（如果是学生且设置了年级，则按年级筛选；否则不筛选年级）
        # 计算每个课程的综合评分：订阅数 * 0.8 + 时间新鲜度 * 0.4
        print('开始构建课程查询')

        # 新增：打印SQL查询语句
        courses_query = db.session.query(
            CourseModel.id,
            CourseModel.name,
            CourseModel.cover,
            CourseModel.created_at,
            CourseModel.price,
            CourseModel.introduction,
            CourseModel.grade_id,
            GradeModel.name.label('grade_name'),
            CourseModel.subject_id,
            SubjectModel.name.label('subject_name'),
            CourseModel.teacher_id,
            UserModel.username.label('teacher_name'),
            func.count(SubscribeModel.id).label('subscriber_count'),
            # 计算时间新鲜度分数（越新的课程分数越高）
            func.datediff(func.now(), CourseModel.created_at).label('days_since_created')
        ).join(
            GradeModel, CourseModel.grade_id == GradeModel.id
        ).join(
            SubjectModel, CourseModel.subject_id == SubjectModel.id
        ).join(
            UserModel, CourseModel.teacher_id == UserModel.id
        ).outerjoin(
            SubscribeModel, CourseModel.id == SubscribeModel.course_id
        )

        # 新增：打印最终SQL查询语句（编译后的）
        compiled_query = str(courses_query.statement.compile(compile_kwargs={"literal_binds": True}))
        print(f'生成的SQL查询语句: {compiled_query}')

        # 如果是学生用户且设置了年级，按年级筛选
        if user_role == 0 and user_grade:
            print(f'按年级筛选课程，年级: {user_grade}')
            courses_query = courses_query.filter(GradeModel.name == user_grade)

            # 新增：打印筛选后的SQL查询语句
            filtered_query = str(courses_query.statement.compile(compile_kwargs={"literal_binds": True}))
            print(f'按年级筛选后的SQL查询: {filtered_query}')
        else:
            print('不进行年级筛选，查询所有年级课程')

        # 执行查询并获取结果
        print('执行课程查询...')
        courses_query_result = courses_query.group_by(CourseModel.id).all()
        print(f'查询完成，返回{len(courses_query_result)}条课程记录')

        # 新增：如果查询结果为空，打印更多调试信息
        if not courses_query_result:
            # 检查基础课程数量
            total_courses = db.session.query(CourseModel).count()

            # 检查年级表数据
            grades = db.session.query(GradeModel).all()
            grade_names = [g.name for g in grades]

            # 检查科目表数据
            subjects = db.session.query(SubjectModel).all()
            subject_names = [s.name for s in subjects]

            # 检查教师表数据
            teachers = db.session.query(UserModel).count()

            return jsonify({
                'success': True,
                'message': '暂无课程可推荐',
                'data': {
                    'courses': [],
                    'total': 0
                }
            }), 200

        # 计算每个课程的综合评分
        print('开始计算课程综合评分')
        courses_with_score = []
        max_subscribers = max(course.subscriber_count for course in courses_query_result) or 1
        min_days = min(course.days_since_created for course in courses_query_result) or 0
        max_days = max(course.days_since_created for course in courses_query_result) or 1

        print(f'订阅数统计: max_subscribers={max_subscribers}')
        print(f'创建时间统计: min_days={min_days}, max_days={max_days}')

        for idx, course in enumerate(courses_query_result):
            # 订阅数评分（0-1）
            subscriber_score = course.subscriber_count / max_subscribers

            # 时间新鲜度评分（0-1，越新分数越高）
            if max_days == min_days:
                time_score = 1.0
            else:
                time_score = 1 - (course.days_since_created - min_days) / (max_days - min_days)

            # 综合评分
            final_score = subscriber_score * 0.8 + time_score * 0.4

            courses_with_score.append({
                'course': course,
                'score': final_score
            })

            # 打印前5个课程的详细评分信息
            if idx < 5:
                print(f'课程ID={course.id}, 名称={course.name}, 订阅数={course.subscriber_count}, '
                      f'创建天数={course.days_since_created}, '
                      f'订阅评分={subscriber_score:.3f}, '
                      f'时间评分={time_score:.3f}, '
                      f'综合评分={final_score:.3f}, '
                      f'年级={course.grade_name}, 科目={course.subject_name}, 教师={course.teacher_name}')

        # 按评分排序，取前12个作为候选池（保证有足够的选择空间）
        print('按综合评分排序课程')
        courses_with_score.sort(key=lambda x: x['score'], reverse=True)
        candidate_courses = courses_with_score[:min(12, len(courses_with_score))]

        print(f'候选课程池大小: {len(candidate_courses)}')
        for i, item in enumerate(candidate_courses[:5]):
            course = item['course']
            print(f'候选课程#{i + 1}: ID={course.id}, 名称={course.name}, 评分={item["score"]:.3f}, '
                  f'订阅数={course.subscriber_count}, 年级={course.grade_name}, 科目={course.subject_name}')

        # 从候选池中随机选择8个课程
        # 使用加权随机选择，评分高的课程被选中的概率更大
        print('开始从候选池中选择推荐课程')
        selected_courses = []

        if len(candidate_courses) <= 8:
            # 如果候选课程不足8个，全部选择
            print(f'候选课程不足8个，直接选择全部 {len(candidate_courses)} 个课程')
            selected_courses = candidate_courses
        else:
            # 权重随机选择
            print(f'候选课程充足，使用加权随机选择8个课程')
            weights = [item['score'] for item in candidate_courses]
            # 添加一定的随机性，避免总是选择相同的课程
            weights = [w + random.uniform(0, 0.3) for w in weights]

            # 使用加权随机选择
            temp_candidates = candidate_courses.copy()
            temp_weights = weights.copy()

            for i in range(8):
                if not temp_candidates:
                    break

                # 计算选择概率
                total_weight = sum(temp_weights)
                probabilities = [w / total_weight for w in temp_weights]

                # 随机选择一个索引
                selected_idx = random.choices(range(len(temp_candidates)), weights=probabilities)[0]
                selected_courses.append(temp_candidates[selected_idx])

                print(f'选择课程#{i + 1}: ID={temp_candidates[selected_idx]["course"].id}, '
                      f'名称={temp_candidates[selected_idx]["course"].name}, '
                      f'评分={temp_candidates[selected_idx]["score"]:.3f}, '
                      f'权重={temp_weights[selected_idx]:.3f}, '
                      f'年级={temp_candidates[selected_idx]["course"].grade_name}')

                # 移除已选择的课程
                temp_candidates.pop(selected_idx)
                temp_weights.pop(selected_idx)

        # 构建返回数据
        print('开始构建返回数据')
        courses_data = []
        for item in selected_courses:
            course = item['course']
            cover_url = course.cover
            if cover_url:
                cover_url = cover_url
                print(f'课程ID={course.id}的封面URL转换结果: {cover_url}')
            else:
                print(f'课程ID={course.id}没有封面图片')

            courses_data.append({
                'id': course.id,
                'name': course.name,
                'cover': cover_url,
                'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'price': course.price,
                'introduction': course.introduction,
                'grade_id': course.grade_id,
                'grade_name': course.grade_name,
                'subject_id': course.subject_id,
                'subject_name': course.subject_name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher_name,
                'subscriber_count': course.subscriber_count,
                'recommend_score': round(item['score'], 3)  # 调试用，可以移除
            })

        # 随机打乱最终结果，增加推荐多样性
        random.shuffle(courses_data)
        print(f'最终推荐课程数量: {len(courses_data)}')
        print(f'最终推荐课程ID列表: {[course["id"] for course in courses_data]}')

        # 构建推荐消息
        if user_role == 0:  # 学生用户
            if user_grade:
                recommend_message = f'成功获取{user_grade}年级的推荐课程！'
            else:
                recommend_message = '成功获取推荐课程！（建议设置年级以获得更精准推荐）'
        else:  # 教师或其他用户
            recommend_message = '成功获取推荐课程！'

        print(f'返回推荐结果: {len(courses_data)}个课程, 用户角色={user_role}, 用户年级={user_grade}')
        return jsonify({
            'success': True,
            'message': recommend_message,
            'data': {
                'courses': courses_data,
                'total': len(courses_data),
                'user_role': user_role,
                'user_grade': user_grade
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500