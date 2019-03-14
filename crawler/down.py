import requests
import time
from bs4 import BeautifulSoup as bs
import sys

def get_login_token(raw_resp):
    soup = bs(raw_resp.text)
    token = [n['value'] for n in soup.find_all('input') if n['name'] == 'authenticity_token']
    #print token
    return token[0]

def get_last_time(raw_resp):
    soup = bs(raw_resp.text)
    last_time = [n['value'] for n in soup.find_all('input') if n['name'] == 'last_time']
    return last_time[0]


payload = {'login' : 'kramatk@gmail.com',
          'password' : 'botbotbot'}

with requests.session() as s:
    resp = s.get('http://ask.fm/')
    payload['authenticity_token'] = get_login_token(resp)
    print "login ",payload['authenticity_token']
    response_post = s.post('http://ask.fm/session',data=payload)

    response = s.get('http://ask.fm/account/stream')

    token = get_login_token(response)
    last_time = get_last_time(response)
    more_data = {'last_time':"1399230336",
            'authenticity_token': token}
    print more_data

    try:
        while True:
            
            r = s.post("http://ask.fm/account/more_stream", data=more_data)
            code = r.text[30:].replace("\n","");
            soup = bs(code)
            div_qst = soup.findAll("div", { "class":"\\\"questionBox\\\"" })
            for div in div_qst:
                try:
                    qst = div.findAll("div", { "class":"\\\"question\\\"" })[0].span.span.contents[0].decode('unicode-escape')
                    ans = div.findAll("div", { "class":"\\\"answer\\\"" })[0].contents[0].decode('unicode-escape')
                    ask_id = div["id"].decode('unicode-escape').replace('\"',"")
                    data = {'id': ask_id,
                            'question': qst.strip(),
                            'answer': ans.strip()}
                    r_add = requests.post("http://simsimi.curve.in.th/add", data=data)

                    if "added" in r_add.text:
                        print "id:",ask_id
                        print "Q: ",qst.strip()
                        print "A: ",ans.strip()
                        print " ----------- "
                    else:
                        print ask_id , 
                        print "already added"

                except Exception as e:
                    print "line ",sys.exc_traceback.tb_lineno 
                    print "error : ",e

            more_data['last_time'] = str(int(more_data['last_time']) - 500)
            #print r.text[-100:]
            print more_data['last_time']
            print " ------- "
            #time.sleep(10)
            #raw_input()
    except Exception as e:
        print e

print "end"