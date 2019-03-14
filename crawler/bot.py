import requests
import time
from bs4 import BeautifulSoup as bs
import sys

def get_login_token(raw_resp):
    soup = bs(raw_resp.text)
    print raw_resp.text
    token = [n['value'] for n in soup.find_all('input') if n['name'] == 'authenticity_token']
    return token[0]


def get_question(raw_resp):
    soup = bs(raw_resp.text)
    div_qst = soup.findAll("div", { "class":"questionBox" })
    for div in div_qst:
        qst_div = div.findAll("div", { "class":"question" })[0]
        ans_div = div.findAll("div", { "class":"answer" })[0]
        
        qst = qst_div.span.span.contents[0]
        ans = ans_div.contents[0]

        data = {'id':div["id"],
                'question': qst.strip(),
                'answer': ans.strip()}

        img = ans_div.findAll("img")
        if len(img) >  0:
            data["img"] = img[0]["src"]


        r = requests.post("http://simsimi.curve.in.th/add", data=data)


        if "added" in r.text:
            print "id:",div["id"]
            print "Q: ",qst.strip()
            print "A: ",ans.strip()
            print " ----------- "
            if data.has_key('img'):
                print "img: ",data["img"]
        else:
            print "already added"
            break
    

while True:


    try:
        payload = {'login' : 'kramatk@gmail.com',
                  'password' : 'botbotbot'}

        with requests.session() as s:
            resp = s.get('http://ask.fm/')
            payload['authenticity_token'] = get_login_token(resp)

            response_post = s.post('http://ask.fm/session',
                               data=payload)
            response = s.get('http://ask.fm/account/stream')
            try:
                get_question(response)
            except Exception as e_qst:
                print "error in qst"
                print e_qst

    except Exception as e:
        print "line ",sys.exc_traceback.tb_lineno 
        print e
        

    #print "end"
    time.sleep(10)