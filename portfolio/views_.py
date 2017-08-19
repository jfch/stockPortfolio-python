from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from .models import UserCreationForm
from yahoo_finance import Share
import time
import heapq
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.http.response import HttpResponse
import json

# Create your views here.
@csrf_exempt
def user_registration_web(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, user)
            return redirect('/portfolio')
    else:
        form = UserCreationForm()
    return render_to_response('portfolio/register.html', {
        'form': form,
    })

@login_required()
def home_page(request):
    return render(request, 'portfolio/home.html')

@login_required()
def result_page(request):
    rstlist = list()
    grow_sortlst = list()
    value_sortlst = list()
    quality_sortlst = list()

    #grow_stcklist = [ 'PNW','RL','PPG','ACN', 'ATVI', 'AYI', 'AMD', 'LNT', 'ALXN', 'GOOGL'] 
    grow_stcklist = ['CVX', 'YHOO', 'YHOO', 'YHOO','YHOO','YHOO','YHOO', 'YHOO', 'YHOO', 'YHOO']
    value_stcklist = ['AMG', 'AFL', 'APD', 'AKAM','PCG','PM','PSX', 'AAP', 'AES', 'AET']
    quality_stcklist = ['MMM', 'ABT', 'ABBV','PEP','PKI','PRGO','PFE', 'ALB', 'ECL', 'AGN']
    stckdict = dict()

    if request.method == 'POST':
        allotment = int(str(request.POST['allotment']))
        ori_allotment = allotment
        iv_type = 0
        for key in request.POST.keys():
            print "iv_type="+str(iv_type)
            print str(key)
            if key in ['ethical','growth','index','quality','value']:
                iv_type = iv_type + 1

        print("current selected types count = " + str(iv_type))
        if iv_type == 2:
            allotment = allotment/float(2)

        if 'ethical' in request.POST.keys():
            AAPL = Share('AAPL')
            aapl_f = float(str(AAPL.get_percent_change_from_year_low())[0:-1]) + \
                     float(str(AAPL.get_percent_change_from_50_day_moving_average())[0:-1]) - \
                     float(str(AAPL.get_percent_change_from_year_high())[0:-1])

            ADBE = Share('ADBE')
            adbe_f = float(str(ADBE.get_percent_change_from_year_low())[0:-1]) + \
                     float(str(ADBE.get_percent_change_from_50_day_moving_average())[0:-1]) - \
                     float(str(ADBE.get_percent_change_from_year_high())[0:-1])

            NSRGY = Share('NSRGY')
            nsrgy_f = float(str(NSRGY.get_percent_change_from_year_low())[0:-1]) + \
                      float(str(NSRGY.get_percent_change_from_50_day_moving_average())[0:-1]) - \
                      float(str(NSRGY.get_percent_change_from_year_high())[0:-1])
            stckdict['AAPL'] = AAPL
            stckdict['ADBE'] = ADBE
            stckdict['NSRGY'] = NSRGY
            total_f = (aapl_f + adbe_f + nsrgy_f)*iv_type
            aapl_pct = aapl_f/float(total_f)
            adbe_pct = adbe_f/float(total_f)
            nsrgy_pct = nsrgy_f/float(total_f)
            aaplD = {"sticker":"AAPL","name":AAPL.get_name(),"aloc_pct":str(aapl_pct),"aloc_amt":str(allotment*aapl_pct),"price":str(AAPL.get_price()),"exchange":str(AAPL.get_stock_exchange())}
            adbeD = {"sticker":"ADBE","name":ADBE.get_name(),"aloc_pct":str(adbe_pct),"aloc_amt":str(allotment*adbe_pct),"price":str(ADBE.get_price()),"exchange":str(ADBE.get_stock_exchange())}
            nsrgyD = {"sticker":"NSRGY","name":NSRGY.get_name(),"aloc_pct":str(nsrgy_pct),"aloc_amt":str(allotment*nsrgy_pct),"price":str(NSRGY.get_price()),"exchange":str(NSRGY.get_stock_exchange())}
            rstlist.append(aaplD)
            rstlist.append(adbeD)
            rstlist.append(nsrgyD)

        if 'growth' in request.POST.keys():
            for stock in grow_stcklist:
                while True:
                    try:
                        detail = Share(stock)			
                    except:
                        time.sleep(0.1)
                        continue
                    break
                stckdict[stock]=detail
                heapq.heappush(grow_sortlst, (float(str(detail.get_percent_change_from_year_low())[0:-1]) +
                                              float(
                                                  str(detail.get_percent_change_from_200_day_moving_average())[0:-1]) +
                                              float(str(detail.get_percent_change_from_50_day_moving_average())[0:-1]) +
                                              float(str(detail.get_percent_change_from_year_high())[0:-1]), stock,
                                              detail))
                if len(grow_sortlst) > 3:
                    heapq.heappop(grow_sortlst)
            total_f = 0
	    print stckdict #"1YES
	    
            for item in grow_sortlst:
                total_f = total_f + item[0]
            for item in grow_sortlst:
                item_pct = item[0]/float(total_f*iv_type)
                item_amt = allotment*item_pct
                rstlist.append({"sticker":item[1],"name":item[2].get_name(),"aloc_pct":str(item_pct),"aloc_amt":str(item_amt),"price":str(item[2].get_price()),"exchange":str(item[2].get_stock_exchange())})
	    
        if 'index' in request.POST.keys():

            VTI = Share('VTI')
            vti_f = float(str(VTI.get_percent_change_from_year_low())[0:-1]) + \
                     float(str(VTI.get_percent_change_from_200_day_moving_average())[0:-1]) - \
                     float(str(VTI.get_percent_change_from_year_high())[0:-1])

            IXUS = Share('IXUS')
            ixus_f = float(str(IXUS.get_percent_change_from_year_low())[0:-1]) + \
                     float(str(IXUS.get_percent_change_from_200_day_moving_average())[0:-1]) - \
                     float(str(IXUS.get_percent_change_from_year_high())[0:-1])

            ILTB = Share('ILTB')
            iltb_f = float(str(ILTB.get_percent_change_from_year_low())[0:-1]) + \
                      float(str(ILTB.get_percent_change_from_200_day_moving_average())[0:-1]) - \
                      float(str(ILTB.get_percent_change_from_year_high())[0:-1])
            stckdict['VTI'] = VTI
            stckdict['IXUS'] = IXUS
            stckdict['ILTB'] = ILTB
            total_f = (vti_f + ixus_f + iltb_f)*iv_type
            vti_pct = vti_f / float(total_f)
            ixus_pct = ixus_f / float(total_f)
            iltb_pct = iltb_f / float(total_f)
            vtiD = {"sticker": "VTI", "name": VTI.get_name(), "aloc_pct": str(vti_pct),
                     "aloc_amt": str(allotment * vti_pct), "price": str(VTI.get_price()),
                     "exchange": str(VTI.get_stock_exchange())}
            ixusD = {"sticker": "IXUS", "name": IXUS.get_name(), "aloc_pct": str(ixus_pct),
                     "aloc_amt": str(allotment * ixus_pct), "price": str(IXUS.get_price()),
                     "exchange": str(IXUS.get_stock_exchange())}
            iltbD = {"sticker": "ILTB", "name": ILTB.get_name(), "aloc_pct": str(iltb_pct),
                      "aloc_amt": str(allotment * iltb_pct), "price": str(ILTB.get_price()),
                      "exchange": str(ILTB.get_stock_exchange())}
            rstlist.append(vtiD)
            rstlist.append(ixusD)
            rstlist.append(iltbD)

        if 'quality' in request.POST.keys():
            for stock in quality_stcklist:
                while True:
                    try:
                        detail = Share(stock)
                    except:
                        time.sleep(0.1)
                        continue
                    break
                stckdict[stock] = detail
                heapq.heappush(quality_sortlst, (
                    float(detail.get_price_earnings_ratio() if detail.get_price_earnings_ratio() != None else 0) +
                    float(
                        detail.get_price_earnings_growth_ratio() if detail.get_price_earnings_growth_ratio() != None else 0) +
                    float(
                        detail.get_change_from_200_day_moving_average() if detail.get_change_from_200_day_moving_average() != None else 0) +
                    float(
                        detail.get_price_earnings_growth_ratio() if detail.get_price_earnings_growth_ratio() != None else 0),
                    stock, detail))
                if len(quality_sortlst) > 3:
                    heapq.heappop(quality_sortlst)
            total_f = 0
            for item in quality_sortlst:
                total_f = total_f + item[0]
            for item in quality_sortlst:
                item_pct = item[0] / float(total_f*iv_type)
                item_amt = allotment * item_pct
                rstlist.append({"sticker": item[1], "name": item[2].get_name(), "aloc_pct": str(item_pct),
                                "aloc_amt": str(item_amt), "price": str(item[2].get_price()),
                                "exchange": str(item[2].get_stock_exchange())})

        if 'value' in request.POST.keys():
            for stock in value_stcklist:
                while True:
                    try:
                        detail = Share(stock)
                    except:
                        time.sleep(0.1)
                        continue
                    break
                stckdict[stock] = detail
                heapq.heappush(value_sortlst,
                               (float(detail.get_dividend_yield() if detail.get_dividend_yield() != None else 0) +
                                float(
                                    detail.get_price_earnings_growth_ratio() if detail.get_price_earnings_growth_ratio() != None else 0) -
                                float(detail.get_price_book() if detail.get_price_book() != None else 0), stock,
                                detail))
                if len(value_sortlst) > 3:
                    heapq.heappop(value_sortlst)
            total_f = 0
            for item in value_sortlst:
                total_f = total_f + item[0]
            print "total_f=" + str(total_f)
            for item in value_sortlst:
                item_pct = item[0] / float(total_f*iv_type)
                item_amt = allotment * item_pct
                rstlist.append({"sticker": item[1], "name": item[2].get_name(), "aloc_pct": str(item_pct),
                                "aloc_amt": str(item_amt), "price": str(item[2].get_price()),
                                "exchange": str(item[2].get_stock_exchange())})
        days_cnt = 16
        str_date =  str((datetime.now() - timedelta(days=days_cnt)).date().isoformat())
	end_date = str((datetime.now() - timedelta(days=1)).date().isoformat())
        #end_date = str(datetime.today().date().isoformat())
        day_pro = list()
        remaining = 0
	
        for item in rstlist:
	    #print "1yes"
            while True:
                try:
		    print "1yesbefor "+item["sticker"]+" "+str_date+" "+end_date
		    #print stckdict[""].get_historical('2017-05-01', '2017-05-16') #"1YES
                    hist_info = stckdict[item["sticker"]].get_historical(str_date,end_date)
                except:
                    time.sleep(0.9)
                    continue
                break
            for i in range(0,6):
		print "1yes:"+str(i)
                if len(day_pro)<=i:
                    day_pro.append({hist_info[i]["Date"]:float(hist_info[i]["Close"])*int(float(item["aloc_amt"])/float(hist_info[i]["Open"]))+float(item["aloc_amt"])%float(hist_info[i]["Open"])})
                else:
                    day_pro[i][hist_info[i]["Date"]] = float(day_pro[i][hist_info[i]["Date"]]) + float(hist_info[i]["Close"])*int(float(item["aloc_amt"])/float(hist_info[i]["Open"])) + float(item["aloc_amt"])%float(hist_info[i]["Open"])
        rstlist.append({"sticker":"portfolio","history":day_pro})
        print(json.dumps(rstlist))
        return render(request, 'portfolio/result.html', {'result': json.dumps(rstlist)})
    return render(request, 'portfolio/home.html')
