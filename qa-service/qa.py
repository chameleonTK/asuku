import json
import collections
import math
import requests
import sys
import os
import random

from time import localtime, strftime, time

sys.path.append(os.path.abspath("kucut"))
from kucut import SimpleKucutWrapper as KUCut

class SparseVector(object):
	def __init__(self):
		self._elem_list = []

	def add_element(self, idx, value):
		self._elem_list.append(idx)
		self._elem_list.append(value)

	# TODO:
	def similarity(self, another_vec):
		def vec_norm(vec):
			sum = 0.0
			for i in range(1, len(vec), 2):
				sum += (int(vec[i])**2)
			return math.sqrt(sum)

		def dot(vec1, vec2):
			v1_idx = 0
			v2_idx = 0
			prod_sum = 0

			if len(vec1) <= 1 or len(vec2) <= 1:
				return 0

			while True:
				#print vec1[v1_idx],"-",vec2[v2_idx]
				if int(vec1[v1_idx]) == int(vec2[v2_idx]):
					prod_sum += (int(vec1[v1_idx+1]) * int(vec2[v2_idx+1]))
					v2_idx += 2
					v1_idx += 2
				elif int(vec1[v1_idx]) > int(vec2[v2_idx]):
					v2_idx += 2
				else:
					v1_idx += 2

				if v2_idx >= len(vec2) or v1_idx >= len(vec1):
					break;
			return prod_sum

		d = dot(self._elem_list, another_vec._elem_list)
		norm = vec_norm(self._elem_list) * vec_norm(another_vec._elem_list)

		if norm == 0:
			return 0
		
		return d/norm

allword_file = open('allword.txt', 'r')
vector_file = open('question_vector.txt', 'r')
default_ans_file = open('default_answer.txt', 'r')
log_file = open('terminal_asksimi_log.txt', 'a')

default_ans = []
for line in default_ans_file:
	default_ans.append(line.replace('\n', ''))

word_idx = {}
for line in allword_file:
	[idx, word] = line.split()
	word_idx[word] = int(idx)

question_vector = {}
for line in vector_file:
	l = line.split()
	qid = l[0]
	vec_len = int(l[1])

	question_vector[qid] = SparseVector()
	#print qid,":",vec_len
	for i in range(2, (vec_len*2)+1, 2):
		question_vector[qid].add_element(l[i], l[i+1])

allword_file.close()
vector_file.close()
default_ans_file.close()

try:
	kucut = KUCut()

	while True:
		raw_question = raw_input()

		answer_start_time = time()
		search_time = 0

		new_question = raw_question.strip()
		new_question = new_question.replace('\n', '')
		result = kucut.tokenize([new_question])[0][0]
		
		qvector = {}
		for word in result:
			word = word.encode('utf-8')

			if word in word_idx:
				#print "word : " + word
				idx = word_idx[word]
				if idx not in qvector:
					qvector[idx] = 1
				else:
					qvector[idx] += 1

		vec = SparseVector()
		newqv = collections.OrderedDict(sorted(qvector.items()))
		for idx, freq in newqv.iteritems():
			vec.add_element(int(idx), int(freq))

		#print "vec", str(vec._elem_list)

		answer_threshold = 0.75
		candidate_qid_list = []
		similarity_list = []

		max_sim = -1
		max_sim_qid = -1
		for qid in question_vector:
			qv = question_vector[qid]
			sim = vec.similarity(qv)
			search_time += 1

			if sim > max_sim:
				max_sim = sim
				max_sim_qid = qid

			if sim > answer_threshold:
				candidate_qid_list.append(qid)
				similarity_list.append(sim)

			if len(candidate_qid_list) >= 5:
				break


		if len(candidate_qid_list) > 0:
			rand_idx = random.randint(0, len(candidate_qid_list)-1)
			max_sim_qid = candidate_qid_list[rand_idx]
			max_sim = similarity_list[rand_idx]

		answer_finish_time = time()

		log_file.write( strftime("%Y-%m-%d %H:%M:%S", localtime()) )
		log_file.write( " Q:[" + raw_question + "]" )

		if max_sim_qid != -1 and max_sim > 0.01:
			req = requests.get("http://simsimi.curve.in.th/ans?id=" + str(max_sim_qid))
			ques_dict = json.loads(req.text)
			ans = ques_dict['answer'].encode('utf-8')
			log_file.write( " A:[" + ans + "] sim:" + str(max_sim) )
			print ans
		else:
			rand_idx = random.randint(0, len(default_ans)-1)
			log_file.write( " A:[" + default_ans[rand_idx] + "] sim:0" )
			print default_ans[rand_idx]

		log_file.write( " compute_time:" + str(answer_finish_time-answer_start_time) )
		log_file.write( " compare_entry:" + str(search_time) )
		log_file.write( '\n' )

except Exception as e:
	print "ERROR : NO ANSWER",e
