#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml import html
from lxml import etree
import requests
import re
import smtplib
import os, sys
from email.mime.text import MIMEText

name_patterns = [".*Nohavica.*",
         ".*Nohavici.*",
         ".*Jaromír.*",
         ".*Jaromíra.*"]

date_patterns = ['.*/01/2018.*',
        '.*/02/2018.*',
        '.*/03/2018.*',
        '.*/04/2018.*',
        '.*/05/2018.*',
        '.*/06/2018.*',
        '.*/07/2018.*',
        '.*/08/2018.*',
        '.*/09/2018.*',
        '.*/10/2018.*',
        '.*/11/2018.*',
        '.*/12/2018.*']
already_sended_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sended.txt")

program = requests.get('http://www.heligonka.cz/program/')
tree = html.fromstring(program.content)
fig_list = tree.xpath('//section[@id="portfolio-filter"]/article/figure/a/figcaption/p/text()')
link_list = tree.xpath('//section[@id="portfolio-filter"]/article/figure/a')

header = "Jaromir Nohavica - Heligonka kontrolor\n"
to_send = ""

def append_already_sended(file, link):
    with open(file, 'a', encoding='utf-8') as f:
        f.write("%s\n" % link)
        
def load_already_sended(file):  
    if os.path.isfile(file):
        already_sended = []
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                already_sended.append(line[:-1])
        return already_sended
    else:
        return None

already_sended = load_already_sended(already_sended_file)
if not already_sended:
    already_sended=""

for date in date_patterns:
    date_pattern = re.compile(date)
    for idx, date in enumerate(fig_list):   
        date_hit = date_pattern.match(date)
        if date_hit:
            if not link_list[idx].attrib["href"] in already_sended:
                performance = requests.get(link_list[idx].attrib["href"])
                tree = html.fromstring(performance.content)
                name_list = tree.xpath('//div[@class="main-content"]/p/text()')
                for text in name_list:
                    #print("%s"%text)
                    for jarek_pattern in name_patterns:
                        jarek_reg = re.compile(jarek_pattern)
                        jarek_hit = jarek_reg.match(text)
                        if jarek_hit:
                            #print(">>> Jarek hraje %s na: %s\n"%(date, link_list[idx].attrib["href"]))
                            to_send += ("Jarek hraje %s na: %s\n" % (date, link_list[idx].attrib["href"]))
                            append_already_sended(already_sended_file, link_list[idx].attrib["href"])
                            break
def get_sender(file):
	with open(file) as f:
		content = f.readlines()
	content = [x.strip() for x in content]
	return (content[0],content[1])
	
def get_receiver(file):
	with open(file) as f:
		content = f.readlines()
		content = [x.strip() for x in content]
	return content	

if to_send:
    to_send = header + to_send
    #print("%s"%to_send)
    
    #get sender mail on one line and his passwd on second line
    sender, pass_sen = get_sender('sender.txt')
    #one line one receiver -> get array
    receiver = get_receiver('receiver.txt')
    
    msg = 'Subject: {}\n\n{}'.format('Heligonka', to_send)
    #msg = MIMEText(to_send)
    #msg['Subject'] = 'Heligonka'
    #msg['From'] = sender
    #msg['To'] = receiver
    
    s = server = smtplib.SMTP('smtp.googlemail.com', 587)
    #s.set_debuglevel(True)
    server.starttls()
    server.ehlo()
    server.login(sender, pass_sen)
    s.sendmail(sender, receiver, msg)
    s.quit()
    
sys.exit(0)
    

