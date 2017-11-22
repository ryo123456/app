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
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib
from concurrent.futures import ThreadPoolExecutor,wait,as_completed
import concurrent.futures

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
				x = count(html, 1)
				hurl = result(html, 6)
				price = hprice(html)
				image = result(html, 9)
				hlocation = result(html, 3)
				htype = result(html,5)
				if x==3:
					purl = parallel(hurl,3,scraping)
					price2 = parallel(hotel,3,js_jtb)
					price3 = parallel(hotel,3,rakuten)
				elif x>=5:
					purl = parallel(hurl,5,scraping)
					price2 = parallel(hotel,5,js_jtb)
					price3 = parallel(hotel,5,rakuten)
					x=5 
				for i in range(x):
					r = re.compile("([^,]*)(/)(.*)")
					try:
						m = r.match("%s"%price2[i])
						ss=m.group(1)+m.group(2)
						price2[i]=ss
					except AttributeError:
						pass
				#print(price2)
				print(price3)
				for i in range(x):
					geo = geocode(hlocation[i + 1])
					dom = xml.dom.minidom.parseString(geo)
					location = dom.getElementsByTagName('location')
					if location.length > 0:
						lat2[i] = location[0].getElementsByTagName('lat')[0].firstChild.data
						lng2[i] = location[0].getElementsByTagName('lng')[0].firstChild.data
				if x == 3:
					index = "index3.html"
				else:
					index = "index.html"

		end = time.time()
		print("\n" +"main"+ str(end-start) + "sec")
	else:
		form = MyForm()
	if x == 3:
		return render(request, 'mapapp/%s' % index, {
			'form': form,
			'html': html,
			'lat': lat,
			'lng': lng,
			'a1': [hotel[1],hotel[2],hotel[3]],
			'a2': [hurl[1],hurl[2],hurl[3]],
			'b1': [image[1],image[2],image[3]],
			'c1': [lat2[0], lat2[1], lat2[2]],
			'c2': [lng2[0], lng2[1], lng2[2]],
			'd1': [price[1],price[2],price[3]],
			'e1': [hlocation[1],hlocation[2],hlocation[3]],
			'f1': [htype[1],htype[2],htype[3]],
			'purl': [purl[0],purl[1],purl[2]]

		})
	else:
		return render(request, 'mapapp/%s' % index, {
			'form': form,
			'html': html,
			'lat': lat,
			'lng': lng,
			'a1': [hotel[1],hotel[2],hotel[3],hotel[4],hotel[5]],
			'a2': [hurl[1],hurl[2],hurl[3],hurl[4],hurl[5]],
			'b1': [image[1],image[2],image[3],image[4],image[5]],
			'c1': [lat2[0], lat2[1], lat2[2], lat2[3], lat2[4]],
			'c2': [lng2[0], lng2[1], lng2[2], lng2[3], lng2[4]],
			'd1': [price[1],price[2],price[3],price[4],price[5]],
			'e1': [hlocation[1],hlocation[2],hlocation[3],hlocation[4],hlocation[5]],
                        'f1': [htype[1],htype[2],htype[3],htype[4],htype[5]],
			'purl': [purl[0],purl[1],purl[2],purl[3],purl[4]]
		

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
	#r = requests.get(url)
	#content_type_encoding = r.encoding if r.encoding != 'ISO-8859-1' else None
	#soup = BeautifulSoup(r.content, 'html.parser', from_encoding=content_type_encoding)
	end = time.time()
	print("\n" +"scraping2 "+ str(end-start) + "sec")
	return url

def parallel(hotel,x,js):
	start = time.time()
	pool = ThreadPoolExecutor(x)
	url=[""]*5
	h=[""]*5
	for i,hotelname in enumerate(hotel):
		if i == 0:
			continue
		elif i > x:
			break
		h[i-1] = pool.submit(js,hotelname)
	for i in range(x):
		url[i] = h[i].result()
	end = time.time()
	print("\n" +"parallel "+ str(end-start) + "sec")
	return url	

def js_jtb(hotel):
	start = time.time()
	driver = webdriver.PhantomJS()
	driver.get('http://www.jtb.co.jp/search/?q=' + urllib.parse.quote_plus(hotel, encoding='utf-8'))
	soup = BeautifulSoup(driver.page_source,"lxml")
	a = soup.find("a", class_="gs-title")
	try:
		href = a['href']
	except KeyError:
		pass
	except TypeError:
		pass
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
	end = time.time()
	print("\n" +"rakuten "+ str(end-start) + "sec")
	return url
