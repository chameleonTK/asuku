import collections
import json
import requests
import sys
import os

sys.path.append(os.path.abspath("kucut"))
from kucut import SimpleKucutWrapper as KUCut

dump_dict = {}
question_pairs = []
req = requests.get("http://simsimi.curve.in.th/all")
ques_dict = json.loads(req.text)
for ask_question in ques_dict:
	ask_question['question'] = ask_question['question'].encode("utf-8")
	ask_question['question'] = ask_question['question'].replace('\n', '')

try:
	kucut = KUCut()

	# simplify vector
	for ask_question in ques_dict:
		qid = ask_question['ask_id']
		question = ask_question['question']

		result = kucut.tokenize([question])[0][0] #
		s = ' | '.join(result)
		print s

except Exception as e:
	print "KUCut Error"

