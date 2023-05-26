import requests
from bs4 import BeautifulSoup
import lxml
#----
import scrapy
import time
from datetime import datetime as dt
import json
import re


class Apteka_scraper(scrapy.Spider):
	name = "Apteka_scraper"
	
	base_url="https://apteka-ot-sklada.ru"
	cat_prefix="/catalog/"
	sort_type="?sort=name"
	
	city_id=92
	
	start_urls = [base_url]

	
	def parse(self, response):
		cats_list_raw=self.get_cats_list()
		cats_list=self.form_cats_plane_dict(cats_list_raw)
		
		prepared=False
		chosen_cats=[]
		
		exists_names=list(cats_list.values())
		exists_slugs=list(cats_list.keys())
				
		while prepared==False:
			answer=input("Введите категории товаров через | (в случае если ранее Вы указали все желаемые категории введите n):\n")
			answer=answer.strip().lower()
			if answer=="n" and len(chosen_cats)>0:
				prepared=True
			else:
				custom_cats=answer.split("|")
				for cat in custom_cats:
					try:
						name_ind=exists_names.index(cat)
					except Exception as ex:
						print("Категории <",cat,"> не существует")
						continue
					
					chosen_cats.append(exists_slugs[name_ind])
		
		chosen_cats=list(map(lambda x: self.base_url+self.cat_prefix+x+self.sort_type,chosen_cats))
				
		for url in chosen_cats:
			yield response.follow(url=url,cookies={"city":92},callback=self.parse_single_cat)

	
	def parse_single_cat(self,response):
		links = response.css("div.ui-card a.goods-card__link::attr(href)").getall()
		
		for link in links:
			yield response.follow(url=link,cookies={"city":92},callback=self.parse_goods_card)
		
		pagination_elems=response.css("ul.ui-pagination__list>li.ui-pagination__page")
		
		pagination_count=len(pagination_elems)
		
		next_li=None
		
		for ind in range(pagination_count):
			if pagination_elems[ind].css("a.ui-pagination__link_active").get()!=None:
				next_li=ind+1
				break
		
		if next_li<pagination_count:
			next_url=pagination_elems[next_li].css("a::attr(href)").get()
			
			yield response.follow(url=next_url,cookies={"city":92},callback=self.parse_single_cat)
	
	
	def parse_goods_card(self,response):
		card_info={
			"timestamp":time.mktime(dt.now().timetuple()),
			"RPC":response.url.split("_")[-1],
			"url":response.url,
			"title":response.css("h1>span::text").get().strip(),
			"marketing_tags":response.css(".goods-tags__list span.ui-tag::text").getall(),
			"brand":response.css(".page-header__description span[itemtype='legalName']::text").get().strip(),
			"section":response.css("ul.ui-breadcrumbs__list span[itemprop='name']::text").getall()
		}
		card_info["marketing_tags"]=list(map(lambda x: x.strip(),card_info["marketing_tags"]))
		card_info["section"]=card_info["section"][2:-1]
		
		card_info["price_data"]=self.form_price_data(response)
		
		card_info["stock"]={
			"in_stock": True if card_info["price_data"]["current"]>0 else False,
			"count": 0 
		}
		
		card_info["assets"]=self.form_assets_data(response)
		
		card_info["metadata"]=self.form_metadata_data(response)
		
		card_info["variants"]=1
		
		yield card_info

	
	def form_price_data(self,resource):
		d={
			"current":0.0,
			"original":0.0,
			"sale_tag":"Скидка {}%"
		}
		
		prices_raw=resource.css(".goods-offer-panel__price>span::text")
		prices=prices_raw.getall()
		
		if len(prices)<1:
			d["sale_tag"]=""
		else:
			for i in range(len(prices)):
				prices[i]=prices[i].strip()
				temp_val=prices[i].split(" ")[:-1]
				prices[i]="".join(temp_val)
				prices[i]=round(float(prices[i]),2)
				
			d["current"]=prices[0]
			
			if len(prices)==1:
				d["original"]=prices[0]
				d["sale_tag"]=""
			elif len(prices)>1:
				d["original"]=prices[1]
				disc=round((d["original"]-d["current"])/d["original"]*100)
				d["sale_tag"]=d["sale_tag"].format(disc)
			
		return d
	
	
	def form_assets_data(self,resource):
		d={
			"main_image":resource.css(".goods-gallery__view img.goods-gallery__picture::attr(src)").get(),
			"set_images":resource.css(".goods-gallery__preview-item img.goods-gallery__picture::attr(src)").getall(),
			"view360": [],
			"video": []
		}
		
		d["main_image"]=self.base_url+d["main_image"]

		d["set_images"]=list(map(lambda x: self.base_url+x,d["set_images"]))
		
		return d

	
	def form_metadata_data(self,resource):
		d={
			"__description":"",
			"СТРАНА ПРОИЗВОДИТЕЛЬ":resource.css(".page-header__description span[itemtype='location']::text").get().strip()
		}
		
		desc=resource.css("section#description .content-text>*").getall()
		
		d["__description"]="".join(desc)
		
		return d

	
	def get_cats_list(self):
		session=requests.session()
		try:
			res=session.get(self.base_url)
			res.raise_for_status()
		except Exception as ex:
			print(ex)
			return []
			
		soup=BeautifulSoup(res.text,"lxml")
		
		js_to_parse=soup.select("body>script")[0]
		
		return self.parse_cats(js_to_parse.text)

		
	def parse_cats(self,js_content):
		json_str="[]"
		
		cats_start_slice=js_content.find("{categories:")
		if cats_start_slice!=-1:
			cats_start_slice+=len("{categories:")
		
		cats_end_slice=js_content.find("},city")
		
		if cats_start_slice!=-1 and cats_end_slice!=-1:
			json_str=js_content[cats_start_slice:cats_end_slice]
			json_str=re.sub(r'id:([^0-9,]+)',r'id:"\1"',json_str)
			json_str=json_str.replace("children:a","children:[]").replace("id:",'"id":').replace("name:",'"name":').replace("slug:",'"slug":').replace("iconUrl:",'"iconUrl":').replace("children:",'"children":')
		
		try:
			json_d=json.loads(json_str)
		except JSONDecodeError as json_er:
			print(json_er.msg)
			json_d=[]
		
		return json_d
	
	
	def form_cats_plane_dict(self,cats,plane_cat={}):
		for i in range(len(cats)):
			plane_cat[cats[i]["slug"]]=cats[i]["name"].lower()
			if len(cats[i]["children"])>0:
				plane_cat=self.form_cats_plane_dict(cats[i]["children"],plane_cat.copy())
		
		return plane_cat