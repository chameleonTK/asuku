
def longest_common_subsequence(word1, word2):
	lenw1 = len(word1)
	lenw2 = len(word2)

	tab = [[0 for x in range(lenw1+1)] for y in range(lenw2+1)]

	for i in range(lenw2):
		for k in range(lenw1):
			cw2 = word2[i]
			cw1 = word1[k]
			if cw1 == cw2:
				tab[i+1][k+1] = tab[i][k] + 1
			else:
				tab[i+1][k+1] = max(tab[i+1][k], tab[i][k+1])

	return tab[lenw2][lenw1]

allword_file = open('allword.txt', 'r')
word_set = []
for line in allword_file:
	[idx, word] = line.split()
	word_set.append(word)

print word_set[0]
print len(word_set[0])

#lcs = longest_common_subsequence("AGCAT", "GAC")
#print lcs
