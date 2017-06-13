from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum, Avg, Count
from .forms import *
import datetime
import time
import calendar
import types
import json
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    account_list = accountbook.objects.all()
    logined_user = request.user
    context = {'account_list':account_list, 'logined_user':logined_user}
    return  render(request, 'accounts/index.html', context)

@login_required
def keepaccount(request):
    logined_user = request.user
    if request.method == 'POST':
        money = int(float(request.POST.get("money"))*100)
        keepaccountform = AccountForm(request.POST)
        who_id = int(request.POST.get("who"))
        who_is = who.objects.get(pk=who_id)
        if keepaccountform.is_valid():
            account = accountbook()
            account.name = keepaccountform.cleaned_data["name"]
            account.user = request.user
            account.money = money
            account.type = keepaccountform.cleaned_data["type"]
            account.who = who_is
            account.date = keepaccountform.cleaned_data["date"]
            account.save()
            url = request.META['HTTP_REFERER']  # HTTP_REFERER 从哪个页面来的回到哪个页面
            return redirect(url)
    else:
        keepaccountform = AccountForm()
        whos = who.objects.filter(user__exact=logined_user)
        context = {'logined_user': logined_user,'keepaccountform': keepaccountform,'whos':whos}
        return render(request, 'accounts/keepaccount.html', context )

@login_required
def summary(request):
    logined_user = request.user
    type_id = request.GET.get("type_id")
    who_id = request.GET.get("who_id")
    month = request.GET.get("month")
    year = request.GET.get("year")
    times = timezone.now()
    kwargs = {
        # 动态查询的字段
    }
    #过滤本月
    day_now = time.localtime()
    day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon)  # 月初肯定是1号
    # calendar.monthrange返回两个值，第一返回为指定月份第一日为星期几（0-6）, 第二返回为此月天数如31
    wday, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
    day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon, monthRange)#day_end 类似 '2017-03-31'
    #构建动态查询，在查询条件包含的字段数不确定的时候非常有用
    if type_id is not None:
        kwargs['type__id']=type_id
    if who_id is not None:
        kwargs['who__id']=who_id
    if year is not None:
        kwargs['date__year']=year
    if month is not None:
       kwargs['date__range']=(day_begin, day_end)
    account_list = accountbook.objects.filter(user__exact=logined_user,**kwargs)
    types = type.objects.all()
    whos = who.objects.filter(user__exact=logined_user)
    #url = request.path
    context = {'account_list': account_list, 'logined_user': logined_user, 'types':types,
               'whos':whos, 'times':times,}
    return  render(request,'accounts/tables.html', context)
#增加开销人
@login_required
def member(request):
    if request.method == 'POST':
        memberform = MemberForm(request.POST)
        if memberform.is_valid():
            member = who()
            member.name = memberform.cleaned_data["name"]
            member.user = request.user
            member.save()
            url = request.META['HTTP_REFERER']  # HTTP_REFERER 从哪个页面来的回到哪个页面
            return redirect(url)
    else:
        memberform = MemberForm()
        return render(request, 'accounts/member.html', {'memberform': memberform})
#设置预算
@login_required
def budgetview(request):
    day_now = time.localtime()
    day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon)
    wday, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
    day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon, monthRange)
    if request.method == 'POST':
        budgetfrom = BudgetForm(request.POST)
        money = int(float(request.POST.get("budget")) * 100)
        if budgetfrom.is_valid():
            try:
                budget_item = budget.objects.get(user=request.user, date__range=(day_begin, day_end)) #如果本月已经设置过预算则修改本月预算
            except ObjectDoesNotExist:
                budget_item = budget()
            budget_item.user = request.user
            budget_item.budget = money
            budget_item.save()
            url = request.META['HTTP_REFERER']  # HTTP_REFERER 从哪个页面来的回到哪个页面
            return redirect(url)
    else:
        try:
            now_budget = budget.objects.get(user=request.user, date__range=(day_begin, day_end)).budget/100
        except ObjectDoesNotExist:
            now_budget = None
        budgetfrom = BudgetForm()
        budget_list = budget.objects.filter(user=request.user,date__lt=day_begin)

        monthCount_sum = \
            accountbook.objects.filter(user=request.user, date__range=(day_begin, day_end)).aggregate(Sum('money'))['money__sum']#本月实际支出
        if monthCount_sum is None:
            monthCount_sum = 0
        if now_budget is not None:
            context = {'budgetform': budgetfrom, 'now_budget':now_budget, 'budget_list':budget_list, 'monthCount_sum':monthCount_sum, 'day_now':datetime.datetime.now()}
        else:
            context = {'budgetform': budgetfrom, 'budget_list':budget_list, 'monthCount_sum':monthCount_sum, 'day_now':datetime.datetime.now()}
        return render(request, 'accounts/budget.html', context)

# 统计模块
@login_required
def monthcount(request):
    # 月份，每月1号统计上月数据
    day_now = time.localtime()
    day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon-1)  # 月初肯定是1号
    # calendar.monthrange 判断由year和month组成某年某也，返回该月第一天为周几和该月总共有多少天,0表示星期一，6表示星期天。
    wday, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon-1)
    day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon-1, monthRange)  # day_end 类似 '2017-03-31'
    for user in NewUser.objects.all():
        for item in type.objects.all():
            monthcount_item = MonthCount()
            monthcount_item.user = user
            monthcount_item.type = item
            #如下一行代码的意思为：按特定条件过滤之后，求某个字段的和。如求指定用户，指定类型，指定时间段的money字段的和。
            # .aggregate(Sum('money'))结果为一个字典（如{'money__sum': 60600}）加上['money__sum']才直接得到值
            monthTypeCount_sum_tmp = accountbook.objects.filter(user=user, type=item, date__range=(day_begin, day_end)).aggregate(Sum('money'))['money__sum']
            if monthTypeCount_sum_tmp is not None:
                monthcount_item.type_sum = monthTypeCount_sum_tmp
                monthcount_item.save()
        monthcountsum_item = MonthCountSum()
        monthcountsum_item.user = user
        monthCount_sum = accountbook.objects.filter(user=user, date__range=(day_begin, day_end)).aggregate(Sum('money'))['money__sum']
        if monthCount_sum is not None:
            monthcountsum_item.sum = monthCount_sum
            monthcountsum_item.save()
    return HttpResponse("OK!")


#统计图表
@login_required
def charts(request):
    logineduser = request.user
    now_year = datetime.datetime.now().strftime('%Y')
    # 上月消费分类占比饼图
    # 取月份日期区间
    day_now = time.localtime()
    last_month_day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon-1)  # 月初肯定是1号, day_now.tm_mon为本月，-1为上个月
    # calendar.monthrange返回两个值，第一返回为指定月份第一日为星期几（0-6）, 第二返回为此月天数如31
    wday, last_month_monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon-1)
    last_month_day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon-1, last_month_monthRange)#day_end 类似 '2017-03-31'
    query_set_month = MonthCount.objects.filter(user=logineduser,date__range=(last_month_day_begin, last_month_day_end))
    # 上月总支出
    last_month_sum = MonthCountSum.objects.get(user=logineduser,date__range=(last_month_day_begin, last_month_day_end)).sum
    month_categorie_dict = {} #定义一个字典用来存分类的值,在模板中遍历字典做为饼子图的name和value
    for item in query_set_month:
        month_categorie_dict[item.type] = item.type_sum

    #本月消费分类占比饼图,实时分析
    day_begin = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon)  # 月初肯定是1号, day_now.tm_mon为本月，-1为上个月
    wday, monthRange = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
    day_end = '%d-%02d-%02d' % (day_now.tm_year, day_now.tm_mon, monthRange)#day_end 类似 '2017-03-31'
    this_month_type_total = accountbook.objects.filter(user=logineduser, date__range=(day_begin, day_end)).aggregate(Sum('money'))[
            'money__sum']   #当月总消费
    if this_month_type_total is None:   #当月消费还没有录入时，上边的this_month_type_total 等于None，会导致后边的错误，所以设置为0
        this_month_type_total = 0
    this_month_type_dict = {} #用字典存储分类支出
    for item in type.objects.all():
        this_month_type_sum=accountbook.objects.filter(user=logineduser, type=item, date__range=(day_begin, day_end)).aggregate(Sum('money'))['money__sum']
        if this_month_type_sum is not None:         #消费为0的不加入到字典中
            this_month_type_dict[item.name] = this_month_type_sum

    #年度分类支出
    this_year_type_total = MonthCount.objects.filter(user=logineduser, date__year=now_year).aggregate(Sum('type_sum'))['type_sum__sum'] #年度总支出
    if this_year_type_total is None:
        this_year_type_total = 0
    this_year_type_dict = {}    #用字典存储分类支出
    for item in type.objects.all():
        this_year_type_sum = MonthCount.objects.filter(user=logineduser, type=item, date__year=now_year).aggregate(Sum('type_sum'))['type_sum__sum']
        if this_year_type_sum is not None:
            this_year_type_dict[item.name] = this_year_type_sum

    #本年度月份汇总趋势折线图
    #支出
    query_set = MonthCountSum.objects.filter(date__year=now_year, user=logineduser).order_by('date') #查询本年度的汇总按月份排序
    d = {}   #定义一个字典用来存月度汇总
    for query_month in query_set:              #循环取出结果集生成字典：d[03] = 10000
        query_month_month = query_month.date.strftime('%m')
        query_month_sum = query_month.sum/100   #转换成元
        d[query_month_month] = query_month_sum
    now_month = datetime.datetime.now().strftime('%m')
    d[now_month] = this_month_type_total/100
    key = d.keys()
    v = d.values()
    categories = list(key)  #字典的key 转换成list传给模板中HighCharts绘图
    data = list(v)          #字典的值 转换成list传给模板中HighCharts绘图
    #预算
    budget_queryset = budget.objects.filter(date__year=now_year, user=logineduser).order_by('date')  # 查询本年度的汇总按月份排序
    x={} #定义一个字典用来存月度支出
    for budget_item in budget_queryset:  # 循环取出结果集生成字典：d[03] = 10000
        budget_item_month = budget_item.date.strftime('%m')
        budget_item_budget = budget_item.budget/100
        x[budget_item_month] = budget_item_budget
    budget_key = list(x.keys())
    budget_data = list(x.values())
    context = {'categories': categories, 'data': data, 'month_categories_dict':month_categorie_dict, 'this_month_type_dict':this_month_type_dict ,
               'this_month_type_total':this_month_type_total, 'last_month_sum':last_month_sum, 'this_year_type_dict':this_year_type_dict,
               'this_year_type_total':this_year_type_total, 'budget_key':budget_key, 'budget_data':budget_data}
    return render(request, 'accounts/charts2.html', context)

#登录模块
def log_in(request):
    if request.method == 'GET':
        loginform = LoginForm()
        return render(request, 'accounts/login.html', {'loginform': loginform})
    if request.method == 'POST':
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data['uid']
            password = loginform.cleaned_data['pwd']
            user = authenticate(username=username, password=password)
            #input_code = request.POST.get('check_code')
            #if input_code.upper() != request.session['CheckCode'].upper():
            #    return render(request, 'login.html', {'form': form, 'error': "验证码错误!"})
            if user is not None:
                login(request, user)
                #url = request.POST.get('source_url')
                #return redirect(url)
                return redirect("/accounts/summary/")
            else:
                return render(request, 'accounts/login.html', {'loginform': loginform, 'error': "用户名或密码错误!"})
        else:
            return render(request, 'accounts/login.html', {'loginform': loginform, 'error': "用户名或密码错误!"})

@login_required
def log_out(request):
    url = request.POST.get('source_url','/accounts/login/')
    logout(request)
    return redirect(url)