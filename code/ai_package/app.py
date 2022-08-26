import ast

from flask import Flask, jsonify
from funcs import recommend, ocr,jobsneedplace,jobssalary,jobslearn,jobsneedcloud,jobsexp,jobsgoodthingcloud,jobsrecommend
from flask import request

app = Flask(__name__)
from flask_cors import CORS
# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')

@app.route('/api/v1/ai/recommend/')   #推荐文本 yes
def test():

    ret = recommend(choicetextid=request.args.get("article_id"))
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/ocr/')  # 身份证识别
def ocr_view():
    ret = ocr(photo=None)
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/place')     #获取工作地点 yes
def jobsneedplace_view():
    ret = jobsneedplace()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})

@app.route('/api/v1/ai/jobsdata/salary')  #获取薪水 yes
def jobssalary_view():
    ret = jobssalary()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/learn')   #获取学历 yes
def jobslearn_view():
    ret = jobslearn()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})

@app.route('/api/v1/ai/jobsdata/experience')   #获取工作经验 yes
def jobsexp_view():
    ret = jobsexp()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})

@app.route('/api/v1/ai/jobsdata/needthing/wordcloud')   #获取需要学习的技能词云
def jobsneed_view():
    ret = jobsneedcloud()
    return ret

@app.route('/api/v1/ai/jobsdata/goodthing/wordcloud')   #获取需要学习的技能词云
def jobsgood_view():
    ret = jobsgoodthingcloud()
    return ret

@app.route('/api/v1/ai/jobsdata/jobrecommend')
def recommend1():
    education: str = request.args.get('education')
    experience: str = request.args.get('experience')
    salary: str = request.args.get('salary')

    try:
        if request.args.get('jobs') is not None:
            jobs: t.Optional[list[str]] = ast.literal_eval(request.args.get('jobs'))
            if not isinstance(jobs, list):
                return jsonify({'code': 400, 'message': 'jobs format error (need a list)'})
            elif len(jobs) > 3:
                return jsonify({'code': 400, 'message': 'up to 3 jobs'})
            elif not all(len(_) <= 50 for _ in jobs):
                return jsonify({'code': 400, 'message': 'some of these jobs is too long (limit 50 characters)'})
        else:
            jobs = None
            print('none!!!!!!!!!!')
    except TypeError as e:  # 需要列表中都是str
        return jsonify({'code': 400, 'message': 'jobs format error (need list[str])'})
    except ValueError as e:  # 传过来的jobs列表字符串有问题
        return jsonify({'code': 400, 'message': 'jobs format error (the list is not safety)'})
    try:
        if request.args.get('city') is not None:
            city: t.Optional[list[str]] = ast.literal_eval(request.args.get('city'))
            if not isinstance(city, list):
                return jsonify({'code': 400, 'message': 'city format error (need a list)'})
            elif len(city) > 3:
                return jsonify({'code': 400, 'message': 'up to 3 city'})
            elif not all(len(_) <= 10 for _ in city):
                return jsonify({'code': 400, 'message': 'some of these city is too long (limit 10 characters)'})
        else:
            city = None
    except TypeError as e:  # 需要列表中都是str
        return jsonify({'code': 400, 'message': 'city format error (need list[str])'})
    except ValueError as e:  # 传过来的city列表字符串有问题
        return jsonify({'code': 400, 'message': 'city format error (the list is not safety)'})
    ret = jobsrecommend(education=education,experience=experience,salary=salary,jobs=jobs,city=city)
    return jsonify({'code': 200, 'message': 'success', 'data': ret})

if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0')
