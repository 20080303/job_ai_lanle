import functools

import img_part
import toml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy(app)
app.config.from_file('config.toml', load=toml.load)


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


def get_one_job():
    return JobsModel.query.filter().first()


xueliranklist = ['不限', '中专', '大专', '本科', '硕士', '博士']
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


def placedeal(where):
    for k, v in area_data.items():
        for i in v:
            if where in i:
                # print(where)
                # print(k)
                return k


def get_select_jobs(education, experience, salary, jobs, city):
    jobst = '%' + jobs + '%'
    temp_jobs = JobsModel.query.filter((JobsModel.job.like(jobst))).limit(60).all()
    temp_copy_jobs = temp_jobs.copy()

    for every_jobs in temp_copy_jobs:
        print(every_jobs.job + ' ')
        print(len(temp_copy_jobs))
        bool = 1
        # exp
        if experience is not None:
            if '不限' in every_jobs.experience:
                bool = 1
            if '一年' in every_jobs.experience and int(experience) <= 1:
                temp_jobs.remove(every_jobs)
                print('expwrong1')
                continue

            if '10年以上' in every_jobs.experience:
                if int(experience) < 10:
                    temp_jobs.remove(every_jobs)
                    print('expwrong2')
                    continue
                else:
                    bool = 1

            try:
                mid = every_jobs.experience.find('-')
                tail = every_jobs.experience.find('年')

                if int(every_jobs.experience[:mid]) <= int(experience):  # exp
                    t = 1
                else:
                    temp_jobs.remove(every_jobs)
                    print('expwrong3')
                    continue

            except:
                if bool == 0:
                    temp_jobs.remove(every_jobs)
                    print('expwrong4')
                    continue
        if salary is not None:
            try:  # salary
                mid = every_jobs.salary.find('-')
                tail = every_jobs.salary.find('k')
                if int(every_jobs.salary[:mid]) <= int(salary) <= int(every_jobs.salary[mid + 1:tail]):
                    t = 1
                else:
                    temp_jobs.remove(every_jobs)
                    print('salarywrong')
                    continue
            except:
                print('salaryerr')
                temp_jobs.remove(every_jobs)
                continue
        if education is not None:
            try:  # edu
                for one in xueliranklist:
                    if one in every_jobs.education:
                        temp_edu_rank = xueliranklist.index(one)

                if temp_edu_rank > xueliranklist.index(education):
                    temp_jobs.remove(every_jobs)
                    print('eduwrong')
                    continue
            except:
                temp_jobs.remove(every_jobs)
                print('eduerr')
                continue
        if city is not None:
            try:  # city
                whichcity = city[0:2]
                if placedeal(whichcity) != placedeal(every_jobs.city[0:2]):
                    temp_jobs.remove(every_jobs)
                    print('citywrong')
                    continue
            except:
                print('cityerr')
                temp_jobs.remove(every_jobs)
                continue

    return temp_jobs


def analysis(jobs):
    jobst = '%' + jobs + '%'
    temp_jobs = JobsModel.query.filter((JobsModel.job.like(jobst))).all()
    salary_dict = {}
    exp_dict = {}
    edu_dict = {'不限': 0, '中专': 0, '大专': 0, '本科': 0, '硕士': 0, '博士': 0}
    city_dict = {}
    for every_jobs in temp_jobs:
        try:  # salary
            mid = every_jobs.salary.find('-')
            tail = every_jobs.salary.find('k')
            salary_temp = (int(every_jobs.salary[:mid]) + int(every_jobs.salary[mid + 1:tail])) / 2
            if salary_temp >= 150:
                salary_temp = salary_temp / 12
            try:
                salary_dict[str(salary_temp)] = salary_dict[str(salary_temp)] + 1
            except:
                salary_dict[str(salary_temp)] = 1
        except:
            print('salary_err')
            continue

        # exp

        try:
            q = every_jobs.experience
            if q == '一年以下':
                q = '1年以下'

            exp_dict[str(q)] = exp_dict[str(q)] + 1
        except:
            q = every_jobs.experience
            if q == '一年以下':
                q = '1年以下'
            exp_dict[str(q)] = 1

        try:  # city
            tempcity = placedeal(every_jobs.city[0:2])
            if tempcity != None:
                try:
                    city_dict[str(tempcity)] = city_dict[str(tempcity)] + 1
                except:
                    city_dict[str(tempcity)] = 1
        except:
            ttt = 0

        # edu
        for one in xueliranklist:
            if one in every_jobs.education:
                try:
                    edu_dict[str(one)] = edu_dict[str(one)] + 1
                except:
                    edu_dict[str(one)] = 1

    data_all = {}
    for one in ['edu', 'exp', 'salary', 'city']:
        data_all[one] = {}
        exec("data_all[one]['name'] = list(" + one + "_dict.keys())")
        exec("data_all[one]['number'] = list(" + one + "_dict.values())")

    zipped = zip((data_all['salary']['name']), data_all['salary']['number'])
    sort_zipped = sorted(zipped, key=lambda x: (float(x[0]), x[1]))

    def to_li_st(tuple_temp, *agrs):
        lst_te_mp = []
        for i in tuple_temp:
            ltemp = list(i)
            ltemp[0] = float(ltemp[0])
            lst_te_mp.append(ltemp)
        return lst_te_mp

    data_all['salary']['data'] = to_li_st(sort_zipped)

    def cmp_edu(t1, t2):
        ranklist = ['不限', '中专', '大专', '本科', '硕士', '博士']
        s1 = t1[0]
        s2 = t2[0]
        if ranklist.index(s1) > ranklist.index(s2):
            return 1

        if ranklist.index(s1) == ranklist.index(s2):
            return 0
        else:
            return -1

    data_all['edu']['name'], data_all['edu']['number'] = zip(
        *sorted(list(zip(data_all['edu']['name'], data_all['edu']['number'])), key=functools.cmp_to_key(cmp_edu)))

    def cmp_exp(t1, t2):
        ranklist = ['经验不限', '1年以下', '1-3年', '3-5年', '5-10年', '10年以上']
        s1 = t1[0]
        s2 = t2[0]
        if ranklist.index(s1) > ranklist.index(s2):
            return 1

        if ranklist.index(s1) == ranklist.index(s2):
            return 0
        else:
            return -1

    data_all['exp']['name'], data_all['exp']['number'] = zip(
        *sorted(list(zip(data_all['exp']['name'], data_all['exp']['number'])), key=functools.cmp_to_key(cmp_exp)))

    return data_all
