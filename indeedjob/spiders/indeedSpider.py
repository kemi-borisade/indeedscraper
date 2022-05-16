#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 00:22:54 2022

@author: oluwakemiborisade
"""

from bs4 import BeautifulSoup
import scrapy

position = 'Data Scientist'
location = "Canada"

#set up start url
url = (f'https://ca.indeed.com/jobs?q={position}&l={location}&sort=date&vjk=fd88b2e4f509dbbb')


class IndeedSpider(scrapy.Spider):
    name = "indeed" #spider name
    start_urls = [url]   
    
    #function to get job description and url for every job
    def parse_jd(self, response, **posting):
        soup = BeautifulSoup(response.text, features="lxml")
        jd = soup.find("div", {"id": "jobDescriptionText"}).get_text()
        url = response.url
        posting.update({"job_description": jd, "url": url}) 
        yield posting
        
    #function to get title, company,summary and location
    def parse(self, response):
        #assign soup object
        soup = BeautifulSoup(response.text, features="lxml")
        listings = soup.find_all('div',{"class":"job_seen_beacon"})
        for listing in listings:
            #extract important info
            job_title = listing.find("h2", {"class": "jobTitle"}).get_text().strip()
            summary = listing.find("div", {"class": "job-snippet"}).get_text().strip()    # strip newlines
            company = listing.find("span", {"class": "companyName"}).get_text().strip()
            location = listing.find("div", {"class": "companyLocation"}).get_text().strip()
            
            #create dictionary of all jobs 
            posting = {"job_title": job_title, "summary": summary, "company": company, "location": location}
            
            #get link for all jobs to extract jd text
            l = listing.find("a", {"class": "jcs-JobTitle"})
            jd_page = l.get("href")
            #check if there is a jd link and follow link and call parse_jd function
            if jd_page is not None:
                #print(jd_page)
                yield response.follow(jd_page, callback=self.parse_jd, cb_kwargs=posting)
         
        #go to the next page if available and repeat scraping process
        page_next = soup.find("a", {"aria-label":  "Next"}).get("href")
        if page_next is not None:
            page_next = response.urljoin(page_next)
            yield scrapy.Request(page_next, callback=self.parse)
    