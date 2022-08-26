import random
import pickle
import numpy as np
import json
import cv2
import numpy as np
from cnocr import CnOcr
import random
from flask import Response, Flask, send_file
from re import L
from shutil import which
from tempfile import TemporaryDirectory
from tkinter.messagebox import NO
from turtle import clear
import difflib
from warnings import warn_explicit
from cv2 import dft
from matplotlib.pyplot import close
import pandas as pd
import numpy as np
from io import StringIO
import re
from sympy import false, true
import tkinter
from usersim import user_sim_recommend_score

def recommend(user_id,choicetextid: str):
    loadData = np.load('test.txt.npy')
    path = 'article.json'
    f = open(path, 'r', encoding='utf-8')
    datatotal = json.load(f)
    totaltext = len(datatotal)  # 文章总数
    p = 1
    for i in range(totaltext):
        if datatotal[i].get("_id").get("$oid") == choicetextid:
            t = i + 1
            p = 0
            break
    if p == 0:
        textsimtotal = loadData[t]
    else:
        textsimtotal = loadData[random.randint(1, 100)]
    temp = []

    try:
        like_list = user_sim_recommend_score(user_id)
    except:
        like_list = []

    for one in np.argsort(-textsimtotal)[1:6]:
        dict = {}
        dict['id'] = (datatotal[one].get("_id").get("$oid"))
        dict['title'] = (datatotal[one].get("title"))
        dict['score'] = textsimtotal[one]
        if dict['title'] in like_list:
            dict['score'] = dict['score'] + 0.5
        temp.append(dict)
    temp = sorted(temp, key=lambda x: x['score'], reverse=True)
    return temp


def ocr(photo):
    img = cv2.imread(photo, 1)

    # 灰度化处理：
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化处理
    ret2, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # binary=cv2.threshold(gray,140,255,1)[1]#二值化函数 草了白字可以 黑字不好
    # cv2.imshow('binary',binary)

    # 膨胀
    kernel = np.ones((6, 6), np.uint8)
    dilate = cv2.dilate(binary, kernel, iterations=4)

    # 轮廓查找
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    ocr = CnOcr()
    for contour in contours:
        epsilon = 0.001
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv2.boundingRect(approx)
        if (w > 3 * h):
            # print(x,y,w,h)
            area = binary[y:(y + h), x:(x + w)]
            # cv2.imshow("test",area)
            res = ocr.ocr_for_single_line(area)
            if len(res[0]) == 18:
                id_num = res[0]
                reliability = res[1]
            else:
                id_num = '请重新咔咔'
                reliability = 0
    return id_num, reliability


def jobsneedplace():
    with open("jobsplacepre.pkl", "rb") as tf:
        new_dict = pickle.load(tf)
    return new_dict


def jobssalary():
    with open("jobssalarypre.pkl", "rb") as tf:
        new_dict = pickle.load(tf)
    return new_dict


def jobslearn():
    with open("jobslearnpre.pkl", "rb") as tf:
        new_dict = pickle.load(tf)
    return new_dict


def jobsexp():
    with open("jobsexppre.pkl", "rb") as tf:
        new_dict = pickle.load(tf)
    return new_dict


def jobsneedcloud():  # 返回需求技能词云
    image = open("needcloud.png")
    # resp = Response(image, mimetype="image/jpeg")
    return send_file('needcloud.png', mimetype='image/gif')


def jobsgoodthingcloud():
    image = open("goodthingcloud.png")
    # resp = Response(image, mimetype="image/jpeg")
    return send_file('goodthingcloud.png', mimetype='image/gif')


def jobsrecommend(salary, jobs, education, experience, city):
    area_data = {
        '北京': ['北京市', '朝阳区', '海淀区', '通州区', '房山区', '丰台区', '昌平区', '大兴区', '顺义区', '西城区',
                 '延庆县', '石景山区', '宣武区', '怀柔区', '崇文区', '密云县',
                 '东城区', '门头沟区', '平谷区'],
        '广东': ['广东省', '东莞市', '广州市', '中山市', '深圳市', '惠州市', '江门市', '珠海市', '汕头市', '佛山市',
                 '湛江市', '河源市', '肇庆市', '潮州市', '清远市', '韶关市', '揭阳市', '阳江市', '云浮市', '茂名市',
                 '梅州市', '汕尾市'],
        '山东': ['山东省', '济南市', '青岛市', '临沂市', '济宁市', '菏泽市', '烟台市', '泰安市', '淄博市', '潍坊市',
                 '日照市', '威海市', '滨州市', '东营市', '聊城市', '德州市', '莱芜市', '枣庄市'],
        '江苏': ['江苏省', '苏州市', '徐州市', '盐城市', '无锡市', '南京市', '南通市', '连云港市', '常州市', '扬州市',
                 '镇江市', '淮安市', '泰州市', '宿迁市'],
        '河南': ['河南省', '郑州市', '南阳市', '新乡市', '安阳市', '洛阳市', '信阳市', '平顶山市', '周口市', '商丘市',
                 '开封市', '焦作市', '驻马店市', '濮阳市', '三门峡市', '漯河市', '许昌市', '鹤壁市', '济源市'],
        '上海': ['上海市', '松江区', '宝山区', '金山区', '嘉定区', '南汇区', '青浦区', '浦东新区', '奉贤区', '闵行区',
                 '徐汇区', '静安区', '黄浦区', '普陀区', '杨浦区', '虹口区', '闸北区', '长宁区', '崇明县', '卢湾区'],
        '河北': ['河北省', '石家庄市', '唐山市', '保定市', '邯郸市', '邢台市', '河北区', '沧州市', '秦皇岛市',
                 '张家口市', '衡水市', '廊坊市', '承德市'],
        '浙江': ['浙江省', '温州市', '宁波市', '杭州市', '台州市', '嘉兴市', '金华市', '湖州市', '绍兴市', '舟山市',
                 '丽水市', '衢州市'],
        '陕西': ['陕西省', '西安市', '咸阳市', '宝鸡市', '汉中市', '渭南市', '安康市', '榆林市', '商洛市', '延安市',
                 '铜川市'],
        '湖南': ['湖南省', '长沙市', '邵阳市', '常德市', '衡阳市', '株洲市', '湘潭市', '永州市', '岳阳市', '怀化市',
                 '郴州市', '娄底市', '益阳市', '张家界市', '湘西州'],
        '重庆': ['重庆市', '江北区', '渝北区', '沙坪坝区', '九龙坡区', '万州区', '永川市', '南岸区', '酉阳县', '北碚区',
                 '涪陵区', '秀山县', '巴南区', '渝中区', '石柱县', '忠县', '合川市', '大渡口区', '开县', '长寿区',
                 '荣昌县', '云阳县', '梁平县', '潼南县', '江津市', '彭水县', '璧山县', '綦江县',
                 '大足县', '黔江区', '巫溪县', '巫山县', '垫江县', '丰都县', '武隆县', '万盛区', '铜梁县', '南川市',
                 '奉节县', '双桥区', '城口县'],
        '福建': ['福建省', '漳州市', '泉州市', '厦门市', '福州市', '莆田市', '宁德市', '三明市', '南平市', '龙岩市'],
        '天津': ['天津市', '和平区', '北辰区', '河北区', '河西区', '西青区', '津南区', '东丽区', '武清区', '宝坻区',
                 '红桥区', '大港区', '汉沽区', '静海县', '宁河县', '塘沽区', '蓟县', '南开区', '河东区'],
        '云南': ['云南省', '昆明市', '红河州', '大理州', '文山州', '德宏州', '曲靖市', '昭通市', '楚雄州', '保山市',
                 '玉溪市', '丽江地区', '临沧地区', '思茅地区', '西双版纳州', '怒江州', '迪庆州'],
        '四川': ['四川省', '成都市', '绵阳市', '广元市', '达州市', '南充市', '德阳市', '广安市', '阿坝州', '巴中市',
                 '遂宁市', '内江市', '凉山州', '攀枝花市', '乐山市', '自贡市', '泸州市', '雅安市', '宜宾市', '资阳市',
                 '眉山市', '甘孜州'],
        '广西': ['广西壮族自治区', '贵港市', '玉林市', '北海市', '南宁市', '柳州市', '桂林市', '梧州市', '钦州市',
                 '来宾市', '河池市', '百色市', '贺州市', '崇左市', '防城港市'],
        '安徽': ['安徽省', '芜湖市', '合肥市', '六安市', '宿州市', '阜阳市', '安庆市', '马鞍山市', '蚌埠市', '淮北市',
                 '淮南市', '宣城市', '黄山市', '铜陵市', '亳州市', '池州市', '巢湖市', '滁州市'],
        '海南': ['海南省', '三亚市', '海口市', '琼海市', '文昌市', '东方市', '昌江县', '陵水县', '乐东县', '五指山市',
                 '保亭县', '澄迈县', '万宁市', '儋州市', '临高县', '白沙县', '定安县', '琼中县', '屯昌县'],
        '江西': ['江西省', '南昌市', '赣州市', '上饶市', '吉安市', '九江市', '新余市', '抚州市', '宜春市', '景德镇市',
                 '萍乡市', '鹰潭市'],
        '湖北': ['湖北省', '武汉市', '宜昌市', '襄樊市', '荆州市', '恩施州', '孝感市', '黄冈市', '十堰市', '咸宁市',
                 '黄石市', '仙桃市', '随州市', '天门市', '荆门市', '潜江市', '鄂州市', '神农架林区'],
        '山西': ['山西省', '太原市', '大同市', '运城市', '长治市', '晋城市', '忻州市', '临汾市', '吕梁市', '晋中市',
                 '阳泉市', '朔州市'],
        '辽宁': ['辽宁省', '大连市', '沈阳市', '丹东市', '辽阳市', '葫芦岛市', '锦州市', '朝阳市', '营口市', '鞍山市',
                 '抚顺市', '阜新市', '本溪市', '盘锦市', '铁岭市'],
        '台湾': ['台湾省', '台北市', '高雄市', '台中市', '新竹市', '基隆市', '台南市', '嘉义市'],
        '黑龙江': ['黑龙江', '齐齐哈尔市', '哈尔滨市', '大庆市', '佳木斯市', '双鸭山市', '牡丹江市', '鸡西市', '黑河市',
                   '绥化市', '鹤岗市', '伊春市', '大兴安岭地区', '七台河市'],
        '内蒙古': ['内蒙古自治区', '赤峰市', '包头市', '通辽市', '呼和浩特市', '乌海市', '鄂尔多斯市', '呼伦贝尔市',
                   '兴安盟', '巴彦淖尔盟', '乌兰察布盟', '锡林郭勒盟', '阿拉善盟'],
        '香港': ["香港", "香港特别行政区"],
        '澳门': ['澳门', '澳门特别行政区'],
        '贵州': ['贵州省', '贵阳市', '黔东南州', '黔南州', '遵义市', '黔西南州', '毕节地区', '铜仁地区', '安顺市',
                 '六盘水市'],
        '甘肃': ['甘肃省', '兰州市', '天水市', '庆阳市', '武威市', '酒泉市', '张掖市', '陇南地区', '白银市', '定西地区',
                 '平凉市', '嘉峪关市', '临夏回族自治州', '金昌市', '甘南州'],
        '青海': ['青海省', '西宁市', '海西州', '海东地区', '海北州', '果洛州', '玉树州', '黄南藏族自治州'],
        '新疆': ['新疆', '新疆维吾尔自治区', '乌鲁木齐市', '伊犁州', '昌吉州', '石河子市', '哈密地区', '阿克苏地区',
                 '巴音郭楞州', '喀什地区', '塔城地区', '克拉玛依市', '和田地区', '阿勒泰州', '吐鲁番地区', '阿拉尔市',
                 '博尔塔拉州', '五家渠市',
                 '克孜勒苏州', '图木舒克市'],
        '西藏': ['西藏区', '拉萨市', '山南地区', '林芝地区', '日喀则地区', '阿里地区', '昌都地区', '那曲地区'],
        '吉林': ['吉林省', '吉林市', '长春市', '白山市', '白城市', '延边州', '松原市', '辽源市', '通化市', '四平市'],
        '宁夏': ['宁夏回族自治区', '银川市', '吴忠市', '中卫市', '石嘴山市', '固原市']
    }

    def jobint(need):
        if '不限' in need:
            return 0
        if '中专' or '中技' in need:
            return 1
        if '大专' in need:
            return 2
        if 'EMBA' in need:
            return 3
        if '本科' in need:
            return 4
        if '硕士' in need:
            return 5
        if '博士' in need:
            return 6

    def string_similar(s1, s2):
        return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

    def needyear(jobyear):
        needyear1 = 0
        if jobyear == '10年以上':
            needyear1 = 10
        if jobyear == '5-10年':
            needyear1 = 5
        if jobyear == '3-5年':
            needyear1 = 3
        if jobyear == '1-3年':
            needyear1 = 1
        if jobyear == '1年以下':
            needyear1 = 0.1
        if jobyear == '经验不限':
            needyear1 = 0
        return needyear1

    def salarydeal(one):
        try:
            first1 = one.find('-')
            firstk = one.find('k')
            lowmoney = int(one[:first1])
            highmoney = int(one[first1 + 1:firstk])
            total = int((lowmoney + highmoney) / 2)
            return total
        except:
            return None

    def placedeal(where):
        for k, v in area_data.items():
            for i in v:
                if where in i:
                    #print(where)
                    #print(k)
                    return k

    cityerr=0
    sign1 = jobs[0]
    try:
        sign2 = jobs[1]
    except:
        sign2 = ''
    wantsalary = salary
    wantlearn = education
    wantexp = experience
    wantwhere = city

    datajobs = pd.read_csv('jobs.csv')
    t = pd.read_csv('jobs_job_url.csv')
    datatype = pd.read_csv('jobs_job_url.csv')['type1'] + pd.read_csv('jobs_job_url.csv')['type2'] + \
               pd.read_csv('jobs_job_url.csv')['type3']
    t = []
    temp = 0
    for one in datatype:
        temp = temp + 1
        if (sign1 == one) or (sign2 == one):
            t.append(temp)

    if len(t) == 0:
        poo = '暂无推荐职位'
        return poo

    # datajobs['num']==(one in t)

    f = StringIO()  # 创建变量指向对象
    recomdjob = []
    for one in t:
        datajobs.loc[datajobs['num'] == one].to_csv(f, mode='a+', index=False, header=False)
    tempjobs = f.getvalue()
    #print(tempjobs)
    for one in tempjobs.split('\n'):
        templistjobmess = re.split(r",(?![^(]*\))", one)
        if len(templistjobmess) <= 4:
            continue
        salarysure = true
        citysure = true
        wtexpsure = true
        wtlearn = true
        wsalary = int(wantsalary)

        try:
            salarygap = abs(wsalary - salarydeal(templistjobmess[2]))
            if salarygap >= 8:
                salarysure = false
        except:
            salarygap = 0
            salaryerr = 1

        try:
            whichcity = wantwhere[0][0:2]
            #print(whichcity+'jhjajd')
            if  (placedeal(whichcity) != placedeal(templistjobmess[3][0:2])):
                #print(placedeal(whichcity)+'   '+placedeal(templistjobmess[3]))
                citysure = false
            #if (templistjobmess[0] == 2):
            #    print(placedeal(whichcity)+'  '+placedeal(templistjobmess[3]))
        except:
            cityerr = cityerr+1
            citysure = false


        jobyear = templistjobmess[4]
        wtexp = int(wantexp)
        if wtexp < needyear(jobyear):
            wtexpsure = false
            #print('no!' + str(wtexp) + '   ' + str(needyear(jobyear)) + ' ' + str(templistjobmess[0]))

            #print('yes!'+str(wtexp) + '   ' + str(needyear(jobyear)) + ' ' + str(templistjobmess[0]))




        needlearnys = templistjobmess[5]
        needlearn = jobint(needlearnys)
        if jobint(wantlearn) < needlearn:
            wtlearn = false

        if (salarysure and citysure and wtexpsure and wtlearn):
            recomdjob.append(one)

    try:
        tempjob = recomdjob[0:9]
    except:
        tempjob = recomdjob
    longjob = []
    for everyone in tempjob:
        dicttemp = {}
        w = everyone.split(',', 6)
        dicttemp['num'] = w[0]
        dicttemp['jobs'] = w[1]
        dicttemp['salary'] = w[2]
        dicttemp['place'] = w[3]
        dicttemp['time'] = w[4]
        dicttemp['learn'] = w[5]

        obj = re.compile("""(?P<rep>.*?)\",\"(?P<rf>.*)""")
        result = obj.finditer(w[6])
        for item in result:
            dicttemp['goodthing'] = item.group('rep').strip('\"').strip('\\').strip('"').strip('"').strip('[').strip(']').replace('\'','').split(',')
            dicttemp['needthing'] = item.group('rf').strip('\"').strip('\\').strip('"').strip('"').strip('[').strip(']').replace('\'','').split(',')
        longjob.append(dicttemp)
    if (len(longjob)!=0):
        return longjob
    else:
        return ("当前无推荐职位")
