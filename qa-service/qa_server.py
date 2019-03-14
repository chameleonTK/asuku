import collections
import math
import sys
import os
import random
import socket

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

		if d <= 0.001:
			return 0

		norm = vec_norm(self._elem_list) * vec_norm(another_vec._elem_list)

		if norm == 0:
			return 0

		return d/norm

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

allword_file = open('allword.txt', 'r')
vector_file = open('question_vector.txt', 'r')
answer_file = open('answer.txt', 'r')
image_file = open('answer_image.txt', 'r')
default_ans_file = open('default_answer.txt', 'r')
log_file = open('asksimi_log.txt', 'a')

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
	for i in range(2, (vec_len*2)+1, 2):
		question_vector[qid].add_element(l[i], l[i+1])

answer_dict = {}
for line in answer_file:
	space_idx = line.index(' ')
	qid = line[:space_idx]
	answer_dict[qid] = line[space_idx+1:].replace('\n', '')

image_dict = {}
for line in image_file:
	space_idx = line.index(' ')
	qid = line[:space_idx]
	image_dict[qid] = line[space_idx+1:]

allword_file.close()
vector_file.close()
default_ans_file.close()
answer_file.close()
image_file.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = ('localhost', 1888)
sock.bind(server_addr)

sock.listen(25)

try:
	kucut = KUCut()

	while True:
		# get new connection
		connection, client_addr = sock.accept()

		try:
			data = connection.recv(5000)
			print 'get question [',data,'] from',client_addr

			answer_start_time = time()
			raw_question = data
			search_time = 0

			new_question = data.strip()
			new_question = preprocess(new_question)
			result = kucut.tokenize([new_question])[0][0]

			qvector = {}
			for word in result:
				word = word.encode('utf-8')

				if word in word_idx:

					word = preprocess_word(word)
					if word == '':
						continue

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
					similarity_list.append(qid)

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
				ans = answer_dict[max_sim_qid]
				log_file.write( " A:[" + ans + "] sim:" + str(max_sim) )
				if qid in image_dict:
					ans += '<br /><img class="answer-image" src="' + image_dict[qid] + '" />'
				print 'ans is',ans
				connection.send( ans )
			else:
				rand_idx = random.randint(0, len(default_ans)-1)
				log_file.write( " A:[" + default_ans[rand_idx] + "] sim:0" )
				print 'ans is',default_ans[rand_idx]
				connection.send( default_ans[rand_idx] )

			log_file.write( " compute_time:" + str(answer_finish_time-answer_start_time) )
			log_file.write( " compare_entry:" + str(search_time) )
			log_file.write( '\n' )

		except Exception as e:
			print "error at",sys.exc_traceback.tb_lineno
			connection.send("Error " + str(e))
		finally:
			connection.close()

except Exception as e:
	print "ERROR :",e

