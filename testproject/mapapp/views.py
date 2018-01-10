# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from .forms import MyForm
from django.views.decorators.csrf import csrf_protect
import geocoder
import urllib.request
import xml.dom.minidom
import xml.etree.ElementTree as ET
import requests
import lxml.html
import time
import signal
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib
from concurrent.futures import ThreadPoolExecutor,wait,as_completed
import concurrent.futures as confu

ghotel = "helloworld"
gcount = 0
gimage = 0
JTB_url = ""
RAKUTEN_url = ""
JALAN_url= ""
jtb_price=[""]*10
rakuten_price=""
jalan_price=[""]*10
ENCODING = 'utf-8'
@csrf_protect
def form_test(request):
	lat=35.689488
	lng=139.691706	  
	form = MyForm()
	return render(request, 'mapapp/index2.html',{
        'form': form,
        'lat': lat,
        'lng': lng,

    })

@csrf_protect
def test(request):
	start = time.time()
	index = "index.html"
	html = 0
	x = 0
	lat = 35.689488
	lng = 139.691706
	hotel = [" "] * 10
	hurl = [" "] * 10
	image = [" "] * 10
	price = [1]*10
	purl = [" "]*10
	lat2 = [1] * 10
	lng2 = [1] * 10

	if request.method == "POST":
		form = MyForm(data=request.POST)

		if form.is_valid():
			w = request.POST['search']
			a = geocode(w)
			dom = xml.dom.minidom.parseString(a)
			location = dom.getElementsByTagName('location')
			if location.length > 0:
				lat = location[0].getElementsByTagName('lat')[0].firstChild.data
				lng = location[0].getElementsByTagName('lng')[0].firstChild.data
				html = jalan(lat, lng)
				hotel = result(html, 1)
				ghotel = hotel
				x = count(html, 1)
				print(x)
				hurl = result(html, 6)
				image = result(html, 9)
				hlocation = result(html, 3)
				if x>=5:
					x = 5
				pric = [hurl,hotel,hotel]
				kansuu = [scraping,js_jtb,rakuten]
				process = parapara(kansuu,x,parallel,pric)
				purl,price2,price3 = process[0],process[1],process[2]
				JTB_url = price2
				RAKUTEN_url = price3
				JALAN_url = purl
				pric = [price2,hotel,hotel]
				kansuu = [jtbscraping,jalanscraping,rscraping]
				process = parapara(kansuu,x,parallel,pric)
				jtb_price = process[0]
				jalan_price = process[1]
				rakuten_price = process[2]


				for i in range(x):
					geo = geocode(hlocation[i + 1])
					dom = xml.dom.minidom.parseString(geo)
					location = dom.getElementsByTagName('location')
					if location.length > 0:
						lat2[i] = location[0].getElementsByTagName('lat')[0].firstChild.data
						lng2[i] = location[0].getElementsByTagName('lng')[0].firstChild.data
				print(jtb_price)
				if x == 2:
					index = "index3.html"
				else:
					index = "index.html"

		end = time.time()
		print("\n" +"main"+ str(end-start) + "sec")
	else:
		form = MyForm()
	if x == 2:
		return render(request, 'mapapp/%s' % index, {
			'form': form,
			'html': html,
			'lat': lat,
			'lng': lng,
			'a1': [hotel[1],hotel[2]],
			'b1': [image[1],image[2]],
			'c1': [lat2[0], lat2[1]],
			'c2': [lng2[0], lng2[1]],
			'd1': [hlocation[1],hlocation[2]],
			'e1': [JALAN_url[1],JALAN_url[2]],
			'e2': [jalan_price[1],jalan_price[1],jalan_price[2],jalan_price[2]],
			'f1': [JTB_url[1],JTB_url[2]],
			'f2': [jtb_price[1][0],jtb_price[1][0],jtb_price[2][0],jtb_price[2][0]],
			'g1': [RAKUTEN_url[1],RAKUTEN_url[2]],
			'g2': [rakuten_price[1][0],rakuten_price[1][1],rakuten_price[2][0],rakuten_price[2][1]]

		})
	else:
		return render(request, 'mapapp/%s' % index, {
			'form': form,
			'html': html,
			'lat': lat,
			'lng': lng,
			'a1': [hotel[1],hotel[2],hotel[3],hotel[4],hotel[5]],
			'b1': [image[1],image[2],image[3],image[4],image[5]],
			'c1': [lat2[0], lat2[1], lat2[2], lat2[3], lat2[4]],
			'c2': [lng2[0], lng2[1], lng2[2], lng2[3], lng2[4]],
			'd1': [hlocation[1],hlocation[2],hlocation[3],hlocation[4],hlocation[5]],
			'e1': [JALAN_url[1],JALAN_url[2],JALAN_url[3],JALAN_url[4],JALAN_url[5]],
			'e2': [jalan_price[1],jalan_price[1],jalan_price[2],jalan_price[2],jalan_price[3],jalan_price[3],jalan_price[4],jalan_price[4],jalan_price[5],jalan_price[5]],
			'f1': [JTB_url[1],JTB_url[2],JTB_url[3],JTB_url[4],JTB_url[5]],
			'f2': [jtb_price[1][0],jtb_price[1][0],jtb_price[2][0],jtb_price[2][0],jtb_price[3][0],jtb_price[3][0],jtb_price[4][0],jtb_price[4][0],jtb_price[5][0],jtb_price[5][0]],
			'g1': [RAKUTEN_url[1],RAKUTEN_url[2],RAKUTEN_url[3],RAKUTEN_url[4],RAKUTEN_url[5]],
			'g2': [rakuten_price[1][0],rakuten_price[1][1],rakuten_price[2][0],rakuten_price[2][1],rakuten_price[3][0],rakuten_price[3][1],rakuten_price[4][0],rakuten_price[4][1],rakuten_price[5][0],rakuten_price[5][1]]
			
					

		})

def geocode(name):
	start = time.time()
	ENCODING = 'utf-8'
	url = u"http://maps.google.com/maps/api/geocode/xml?&language=ja&sensor=false&region=ja&address="

	url = url + urllib.parse.quote(name.encode(ENCODING))
	
	buffer = urllib.request.urlopen(url).read()
	end = time.time()
	print("\n" +"geocode "+ str(end-start) + "sec")
	return buffer

def jalan(lat,lng):
	start = time.time()
	lat = float(lat) * 1.000106961 - float(lat) * 0.000017467 - 0.004602017
	lng = float(lng) * 1.000083049 + float(lng) * 0.000046047 - 0.010041046
	lat = lat * 3600 * 1000
	lng = lng * 3600 * 1000
	lat = int(lat)
	lng = int(lng)
	url = "http://jws.jalan.net/APIAdvance/HotelSearch/V1/"
	api_key = "and15e316b9f30"
	range = 10
	url = url +  "?order=4&xml_ptn=1&pict_size=0&key=" + api_key + "&x=" + str(lng) +"&y=" + str(lat) + "&range=" + str(range)
	html = urllib.request.urlopen(url).read()
	end = time.time()
	print("\n" +"jalan "+ str(end-start) + "sec")
	return html


def result(html,x):
	start = time.time()
	root=ET.fromstring(html)
	i=4
	hotel = ["A"]
	for a in root:
		tag=a.tag
		if tag=="{jws}Hotel":
			hotel.append(root[i][x].text)
			i+=1
	end = time.time()
	print("\n" +"result "+ str(end-start) + "sec")
	return hotel



def count(html,x):
	start = time.time()
	root=ET.fromstring(html)
	i=4
	hotel = ["A"]
	x=0
	for a in root:
		tag=a.tag
		if tag=="{jws}Hotel":
			hotel.append(root[i][x].text)
			i+=1
			x+=1
	end = time.time()
	print("\n" +"count "+ str(end-start) + "sec")
	return x

def hprice(html):
	start = time.time()
	root=ET.fromstring(html)
	i=4
	price = [" "]
	x=0
	for a in root:
		tag=a.tag
		tag2=a.tag
		x=0
		if tag=="{jws}Hotel":
			while tag2 != "{jws}SampleRateFrom":
				x+=1
				tag2 = root[i][x].tag
			price.append(root[i][x].text)
			i+=1
	end = time.time()
	print("\n" +"hprice "+ str(end-start) + "sec")
	return price

def scraping(hurl):
	start = time.time()
	r = requests.get('%s'%hurl)
	content_type_encoding = r.encoding if r.encoding != 'ISO-8859-1' else None
	soup = BeautifulSoup(r.content, 'html.parser', from_encoding=content_type_encoding)
	for link in soup.find_all("link", rel="canonical"):
		purl=link['href']
	url = purl + "plan/"
	end = time.time()
	print("\n" +"scraping2 "+ str(end-start) + "sec")
	return url

def parallel(hotel,x,js):
	start = time.time()
	pool = ThreadPoolExecutor(x)
	url=[""]*7
	h=[""]*7
	for i,hotelname in enumerate(hotel):
		if i == 0:
			continue
		elif i > x:
			break
		h[i-1] = pool.submit(js,hotelname)
	for i in range(x):
		url[i+1] = h[i].result()
	end = time.time()
	print("\n" +"parallel "+ str(end-start) + "sec")
	return url	

def parapara(kansuu,x,parallel,hotel):
	c = [""]*10
	d = [""]*10
	pool = ThreadPoolExecutor(3)
	for i,k in enumerate(kansuu):
		c[i] = pool.submit(parallel,hotel[i],x,k)
	for i in range(3):
		d[i] = c[i].result()
	return d

def js_jtb(hotel):
	start = time.time()
	driver = webdriver.PhantomJS()
	hotel = hotel.replace('　','')
	hotel2 = hotel.split("（")
	hotel = hotel2[0]
	driver.get('http://www.jtb.co.jp/search/?q=' + urllib.parse.quote_plus(hotel, encoding='utf-8'))
	soup = BeautifulSoup(driver.page_source,"lxml")
	a = soup.find("a", class_="gs-title")
	try:
		href = a['href']
		if href.find("dom") != -1:
			wq = soup.find_all("a", class_="gs-title")
			wq = wq[2]
			href = wq['href']
	except KeyError:
		pass
	except TypeError:
		pass
	if 'purl' in locals():
		url = 1
	else:
		url = href
	driver.service.process.send_signal(signal.SIGTERM)
	driver.quit()
	end = time.time()
	print("\n" +"js_jtb "+ str(end-start) + "sec")
	return url

def rakuten(hotel):
	start = time.time()
	num=0
	hurl = "https://kw.travel.rakuten.co.jp/keyword/Search.do?charset=utf-8&f_max=30&lid=topC_search_keyword&f_query=" + urllib.parse.quote_plus(hotel, encoding='utf-8')
	r = requests.get('%s'%hurl)
	soup = BeautifulSoup(r.content,"html.parser")
	for div in soup.select('div > h2 > a'):	
		try:
			purl=div['href']
			purl="https:" + purl
		except KeyError:
			pass
		except TypeError:
			pass
		if 'purl' in locals():
			break
	try:
		r2 = requests.get('%s'%purl) 
		soup2 = BeautifulSoup(r2.content,"lxml")
		for a in soup2.find_all("a",class_="rtconds"):
			try:
				href = a['href']
			except KeyError:
				pass
			except TypeError:
				pass
			if num == 1:
				break
			num+=1
		url = href
	except UnboundLocalError:
		url = 1
	end = time.time()
	print("\n" +"rakuten "+ str(end-start) + "sec")
	return url

def jtbscraping(jtbinfo):
	cnt = 0
	start = time.time()
	r = requests.get('%s'%jtbinfo)
	soup = BeautifulSoup(r.content,"html.parser")
	name = soup.select("div#htl_titleTop > h1")
	name = name[0].text
	regex=r'（.*）'
	name = re.sub(regex,"",name)
	jtb_price = [0,0]
	jtbinfo = list(jtbinfo)
	jtbinfo.pop()
	for a in range(len(jtbinfo)):
		b = jtbinfo.pop()
		if b == "/":
			if jtbinfo.count("/") == 8:
				break				
	jtbinfo = ''.join(jtbinfo)
	r = requests.get('%s'%jtbinfo)
	soup = BeautifulSoup(r.content,"html.parser")
	for a in soup.select("#shisetsu_list > div > div.htl_title > div > h2 > a > span"):
		if name == a.text:
			print(a.text)
			price = soup.select("#shisetsu_list > div > div.htl_listInner > div.htl_body > div > dl.htl_price1 > dd > span")
			jtb_price = price[cnt].text
			jtb_price = jtb_price.replace('\n','')
			jtb_price = list(jtb_price)
			jtb_price[jtb_price.index("円")+1] = ":"
			jtb_price = ''.join(jtb_price)
			jtb_price = jtb_price.split(":")
		cnt+=1
	end = time.time()
	print(jtb_price)
	print("\n" +"jtbscraping"+ str(end-start) + "sec")
	return jtb_price

def jalanscraping(hurl):
	start = time.time()
	print(hurl)
	hurl = hurl.replace('　','')
	hurl = hurl.replace('－','')
	url = "https://www.jalan.net/uw/uwp2011/uww2011init.do?keyword=" +  urllib.parse.quote_plus(hurl,encoding='shift_jis')
	jaran_price = [0,1000000000000]
	r = requests.get('%s'%url)
	soup = BeautifulSoup(r.content,"html.parser")
	div = soup.select('div#fw > div.result > div.detail.clearfix > div.detail-r > div.price.clearfix > span.bold')
	jaran_price = div[0].text
	jaran_price = jaran_price.replace('￥','')
	jaran_price = jaran_price.replace('/人','')
	jaran_price = jaran_price[:-1]
	jaran_price = jaran_price + "円"
	end = time.time()
	print(jaran_price)
	print("\n" +"jaranscraping"+ str(end-start) + "sec")
	return jaran_price

def rscraping(url):
	start = time.time()
	hello = [10000000,0]
	url = "https://kw.travel.rakuten.co.jp/keyword/Search.do?charset=utf-8&f_max=30&lid=topC_search_keyword&f_query=" + url 
	try:
		#url = "https:" + url
		r = requests.get('%s'%url)
		soup = BeautifulSoup(r.content,"html.parser")
		b = soup.select('div#result > div.hotelBox > dl.price > dd > em')
		hello[0] = b[0].text
		price = hello[0].split("円")
		hello[0] = price[0] + "円"
	except:
		pass
	end = time.time()
	print("\n" +"rscraping "+ str(end-start) + "sec")
	return hello

