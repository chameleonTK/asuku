#!/usr/bin/python
#-*-coding: utf-8 -*-

import collections
import json
import requests
import sys
import os

sys.path.append(os.path.abspath("kucut"))
from kucut import SimpleKucutWrapper as KUCut

def preprocess(question):
	question = question.decode('utf-8')
	ret_question = ""
	for c in question:
		if c in "{}[]#$*,;\"\n!:?~()></\\'^":
			ret_question += ' '
		else:
			ret_question += c
	return ret_question.encode('utf-8').lower()

def preprocess_word(word):

	if word[:3] == '555':
		return '555'

	if len(word) > 100:
		return ''

	# if can cast to float return ''
	try:
		f = float(word)
		return ''
	except ValueError:
		pass

	"""
	# TODO: if size is more than X return ''
	notfirst_char = "-." # TODO: add thai character
	while len(word) > 0 and word[0] in notfirst_char:
		del word[0]
	"""

	return word

def count_unique_char(word):
	char_set = set()
	for ch in word:
		char_set.add(ch)
	return len(char_set)

word_freq = {}
simplified_word = {}
simplified_word_count = 0
new_word = set()

# TODO: change to trie
dict_file = open('lexitron.txt')
for word in dict_file:
	utf_word = unicode(word,"tis-620").encode("utf-8")
	utf_word = utf_word.replace('\n', '')
	word_freq[utf_word] = 0
vector_file = open('question_vector.txt', 'w')
allword_file = open('allword.txt', 'w')
answer_file = open('answer.txt', 'w')
image_file = open('answer_image.txt', 'w')


dump_dict = {}
answer_dict = {}
image_dict = {}
question_pairs = []
req = requests.get("http://simsimi.curve.in.th/all?n=0")
json_data = json.loads(req.text)
dict_data = json_data["data"]
next_data = json_data["next"]
ques_dict = []

while len(dict_data) > 0:
	for i in range(len(dict_data)):
		ask_question = dict_data[i]
		ask_question['question'] = ask_question['question'].encode("utf-8")
		ask_question['question'] = preprocess(ask_question['question'])
		answer_dict[ask_question['ask_id']] = ask_question['answer'].encode("utf-8").replace('\n', '')
	
		ques_dict.append(ask_question)
		#if ask_question['image'] != None:
		#	image_dict[ask_question['ask_id']] = ask_question['image']
	
	req = requests.get("http://simsimi.curve.in.th/all?n="+str(next_data))
	json_data = json.loads(req.text)
	dict_data = json_data["data"]
	next_data = json_data["next"]
	#print next_data,len(answer_dict)

print "get data complete"

# remove large question
ques_dict = [q for q in ques_dict if len(q['question']) <= 450]

try:
	kucut = KUCut()
	non_zero_freq_word_count = 0

	# simplify vector
	for ask_question in ques_dict:
		qid = ask_question['ask_id']
		question = ask_question['question']

		result = kucut.tokenize([question])[0][0] #
		for word in result:

			word = preprocess_word(word)
			if word == '':
				continue

			# in dict
			if word in word_freq:
				word_freq[word] += 1
				non_zero_freq_word_count += 1
			# is complex enough to be new word
			elif count_unique_char(word) >= 2 or word == '555':
				word_freq[word] = 1
				non_zero_freq_word_count += 1
				new_word.add(word)

	stop_word_ratio = 0.02 # TODO: change this
	for word in word_freq:
		if word_freq[word] > 0: #and word_freq[word]/float(non_zero_freq_word_count) < stop_word_ratio:
			simplified_word[word] = simplified_word_count
			try:
				allword_file.write((str(simplified_word_count) + " " + word + "\n").encode('utf-8'))
			except Exception as e:
				print "Error in word " + word + " (not write to file)"
			simplified_word_count += 1

	data_count = 0

	# generated vector and store to file
	for ask_question in ques_dict:
		qid = ask_question['ask_id']
		question = ask_question['question']

		# TODO: change to use tf-idf

		qvector = {}
		
		# TODO: preprocess question, remove symbol, etc.

		result = kucut.tokenize([question])[0][0] #
		
		for word in result:
			if word in simplified_word: 
				idx = simplified_word[word]
				if idx not in qvector:
					qvector[idx] = 1
				else:
					qvector[idx] += 1

		if len(qvector) > 0:
			qv = collections.OrderedDict(sorted(qvector.items()))
			vec_str = str(qid) + " " + str(len(qvector))
			for idx, freq in qv.iteritems():
				vec_str += " " + str(idx) + " " + str(freq)
			vec_str += "\n"

			vector_file.write(vec_str)
			data_count += 1

			answer_file.write(str(qid) + " ")
			answer_file.write(answer_dict[qid] + "\n")

			if qid in image_dict:
				image_file.write(str(qid) + " ")
				image_file.write(image_dict[qid] + "\n")

	print "We have",data_count,"question data"

except Exception as e:
	print "Error",e,"at line",sys.exc_traceback.tb_lineno

finally:
	answer_file.close()
	dict_file.close()
	vector_file.close()
	allword_file.close()
	sys.exit()

