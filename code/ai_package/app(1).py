import os
import ast
import toml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from funcs import recommend, ocr, jobsneedplace, jobssalary, jobslearn, jobsneedcloud, jobsexp, jobsgoodthingcloud, \
    jobsrecommend
from flask import request
from jobsv2 import analysis, get_select_jobs
from flask_cors import CORS
import img_part
import pymysql
from cnocr import CnOcr
import ssl
import requests
import json

app = Flask(__name__)
# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')

db = SQLAlchemy(app)
app.config.from_file('config.toml', load=toml.load)


@app.route('/api/v1/ai/recommend/')  # 推荐文本 yes
def test():
    artid = request.args.get("article_id")
    try:
        now_user_id = request.args.get("user_id")
        ret = recommend(user_id=now_user_id, choicetextid=artid)
    except:
        ret = recommend(user_id=None, choicetextid=artid)
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/ocr/')  # 身份证识别 已废弃
def ocr_view():
    ret = ocr(photo=None)
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/place')  # 获取工作地点 yes
def jobsneedplace_view():
    ret = jobsneedplace()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/salary')  # 获取薪水 yes
def jobssalary_view():
    ret = jobssalary()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/learn')  # 获取学历 yes
def jobslearn_view():
    ret = jobslearn()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/experience')  # 获取工作经验 yes
def jobsexp_view():
    ret = jobsexp()
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


@app.route('/api/v1/ai/jobsdata/needthing/wordcloud')  # 获取需要学习的技能词云
def jobsneed_view():
    ret = jobsneedcloud()
    return ret


@app.route('/api/v1/ai/jobsdata/goodthing/wordcloud')  # 获取需要学习的技能词云
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
    ret = jobsrecommend(education=education, experience=experience, salary=salary, jobs=jobs, city=city)
    return jsonify({'code': 200, 'message': 'success', 'data': ret})


class JobsModel(db.Model):
    __tablename__ = 'jobdetail'
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job = db.Column(db.String(20))
    city = db.Column(db.String(15))
    salary = db.Column(db.String(15))
    education = db.Column(db.String(10))
    experience = db.Column(db.String(10))
    goodList = db.Column(db.Text)
    needList = db.Column(db.Text)
    jobInfo = db.Column(db.Text)
    company = db.Column(db.String(20))
    companyType = db.Column(db.String(15))
    companyPeople = db.Column(db.String(15))
    companyPosition = db.Column(db.Text)
    companyInfo = db.Column(db.Text)


@app.route('/api/v1/ai/jobsdata/jobrecommend1')
def recommend2():
    education: str = request.args.get('education')
    experience: str = request.args.get('experience')
    jobs: str = request.args.get('jobs')
    city: str = request.args.get('city')
    salary: str = request.args.get('salary')
    t = get_select_jobs(education, experience, salary, jobs, city)
    listjob = []
    for everyjob in t:
        dict = {}
        dict['number'] = everyjob.number
        dict['job'] = everyjob.job
        dict['city'] = everyjob.city
        dict['salary'] = everyjob.salary
        dict['education'] = everyjob.education
        dict['experience'] = everyjob.experience
        dict['goodList'] = everyjob.goodList
        dict['needList'] = everyjob.needList
        dict['jobInfo'] = everyjob.jobInfo
        dict['company'] = everyjob.company
        dict['companyType'] = everyjob.companyType
        dict['companyPeople'] = everyjob.companyPeople
        dict['companyPosition'] = everyjob.companyPosition
        dict['companyInfo'] = everyjob.companyInfo
        listjob.append(dict)
    return jsonify({'code': 200, 'message': 'success', 'data': listjob})


@app.route('/api/v1/ai/jobsdata/analysis')
def analysis_jobs():
    jobs: str = request.args.get('jobs')
    t = analysis(jobs)
    return jsonify({'code': 200, 'message': 'success', 'data': t})


@app.route('/api/v1/ai/user/id_photo', methods=['POST'])
def save_photo():
    ff = request.files['file']
    save_path = './'
    ff.save(os.path.join(save_path, 'test.jpg'))
    photolist, numbers = img_part.partimg()
    ocr = CnOcr()
    out = ocr.ocr_for_single_line(numbers)
    dict_sfz = {}
    dict_sfz['number'] = out[0].replace(' ', '')
    for photo in photolist:
        out = ocr.ocr_for_single_line(photo)
        print(str(out[0]))
        if len(str(out[0])) >= 2:
            dict_sfz['name'] = out[0].replace('姓名', '')
            dict_sfz['name'] = dict_sfz['name'].replace(':之', '')
            break
    if (len(dict_sfz['number']) != 18) or (dict_sfz['name'] == ''):
        return jsonify({'code': 500, 'message': '请持稳设备拍照捏'})

    def reqeustID(name, idNo):
        url = 'https://eid.shumaidata.com/eid/check'
        params = {
            'idcard': idNo,  # 身份证号码
            'name': name  # 姓名
        }
        appcode = 'b886fd0084854555bc820e14927632ef'  # 服务购买成功之后，点击跳转至阿里云控制台可看到AppCode
        headers = {"Authorization": "APPCODE " + appcode}
        resp = requests.post(url=url, params=params, headers=headers)
        print(resp.text)

        return str(resp.text)

    data_p = reqeustID(dict_sfz['name'], dict_sfz['number'])
    if '"res":"1"' in data_p:
        return jsonify({'code': 200, 'message': 'success', 'data': dict_sfz})
    else:
        return jsonify({'code': 400, 'message': '身份证未通过验证'})


if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0')
