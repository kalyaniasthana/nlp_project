import glob
import matplotlib.pyplot as plt
import os 
import re
import sys


class Dataset:
	def __init__(self, data_path):
		self.data_path = data_path
		self.data = {}
		self.writers = set()
		self.sources = set()
		self.texts_by_writer = {}
		self.length_word_writer_article = {}
		self.puncts = ('!', "," ,"\'" ,";" ,"\"", ".", "-" ,"?")
		self.avg_puncts = {}

	def create_dataset(self):
		for root, dirs, files in os.walk(self.data_path):
			for file in files:
				if(file.endswith(".txt")):
					file_path = os.path.join(root,file)
					root_split = root.strip('\n').split('/')
					self.data[file_path] = {}
					# print(root_split)
					with open(file_path, 'r') as f:
						lines = f.readlines()
						self.data[file_path]['Source'] = root_split[1]
						self.data[file_path]['Writer'] = root_split[2]
						self.data[file_path]['Title'] = lines[0]

						self.data[file_path]['Text'] = ''.join(lines[1:])
						self.writers.add(root_split[2])
						self.sources.add(root_split[1])


	def group_texts_by_writer(self):
		self.texts_by_writer = {writer: [] for writer in self.writers}
		for file_path in self.data:
			self.texts_by_writer[self.data[file_path]['Writer']].append(self.data[file_path]['Text'])

		return self.texts_by_writer

	def avg_length_by_word(self, texts): # use with avg_article_length_by_word
		def calculate(text):

			text = text.strip('\n')
			text = text.replace(',', '')
			text = text.replace('.', '')
			text = text.replace('!', '')
			text = text.replace('?', '')
			text = re.split(' |\n\n|\n', text)
			return len(text)
		sum_ = 0
		for text in texts:
			sum_+= calculate(text)
		return sum_/len(texts)

	# def avg_length_by_word2(self, text):

	# 	texts = re.split('\n|.|\n\n', text)
	# 	def calculate(text):

	# 		text = text.strip('\n')
	# 		text = text.replace(',', '')
	# 		text = text.replace('.', '')
	# 		text = text.replace('!', '')
	# 		text = text.replace('?', '')
	# 		text = re.split('\n|.', text)
	# 		return len(text)
	# 	sum_ = 0
	# 	for text in texts:
	# 		sum_+= calculate(text)
	# 	return sum_/len(texts)


	def avg_article_length_by_word(self):
		self.length_word_writer_article = {writer: 0 for writer in self.texts_by_writer}
		for writer in self.texts_by_writer:
			texts = self.texts_by_writer[writer]
			self.length_word_writer_article[writer] = self.avg_length_by_word(texts)
		return self.length_word_writer_article


	def plot_avg_article_length_by_word(self):

		x = self.length_word_writer_article.keys()
		y = [*self.length_word_writer_article.values()]
		plt.bar(x, y)
		# plt.yticks(y, rotation=45)
		plt.xticks(rotation=90)
		plt.plot()
		plt.savefig('visualizations/avg_article_length_by_word_by_writer.pdf', bbox_inches='tight')

	# def avg_sentence_length_by_word(self):
	# 	self.length_word_writer_sentence = {writer: 0 for writer in self.texts_by_writer}
	# 	for writer in self.texts_by_writer:
	# 		texts = self.texts_by_writer[writer]
	# 		for text in texts:
	# 			self.length_word_writer_sentence[writer] += self.avg_length_by_word2(text)
	# 		# self.length_word_writer_sentence[writer] /=len(texts)
	# 	return self.length_word_writer_sentence

	def count_punctuations_in_article(self, text):
		count = 0
		for i in range(len(text)):
			if text[i] in self.puncts:
				# print(text[i])
				count += 1
		return count

	def avg_num_punctuations(self):
		self.avg_puncts = {writer: 0 for writer in self.texts_by_writer}
		for writer in self.texts_by_writer:
			texts = self.texts_by_writer[writer]
			count = 0
			for text in texts:
				count += self.count_punctuations_in_article(text)
			self.avg_puncts[writer] = count/len(texts)
		return self.avg_puncts

	def plot_avg_num_punctuations(self):

		x = self.avg_puncts.keys()
		y = [*self.avg_puncts.values()]
		plt.bar(x, y)
		# plt.yticks(y, rotation=45)
		plt.xticks(rotation=90)
		plt.plot()
		plt.savefig('visualizations/avg_puncts_by_writer.pdf', bbox_inches='tight')



	# for testing purposes only
	# def do_something(self):
	# 	texts = []
	# 	for key in self.data:
	# 		text = self.data[key]['Text']
	# 		texts.append(text)

	# 	return self.avg_sentence_length_by_word(texts)
	

	def get_data(self):
		return self.data


if __name__ == '__main__':
	dataset = Dataset('data')
	dataset.create_dataset()
	dataset.group_texts_by_writer()
	dataset.avg_num_punctuations()
	dataset.plot_avg_num_punctuations()
	# print(dataset.avg_article_length_by_word())
	# dataset.plot_avg_article_length_by_word()
	# # print(dataset.avg_sentence_length_by_word())