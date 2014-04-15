# file: utilities.py 
# Winthrop Gillis (wgillis)
# 4/9/2014
# This file contains utility functions for certain tasks needed =
# by the web app

# import any needed libraries
import random, string

def generateURL():
	return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(25))

# this gets the picture name associated with each tag
# def getTag(tag):
# 	tags = {'neuroscience': 'brain.png', 'biology': 'microscope.png',
# 				'science': 'atom.png', 'systems-dynamics': 'lorenz.jpg'}
# 	if tag in tags:
# 		pic = tags[tag]

# 	else:
# 		pic = 'article.png'

# 	return pic

def selectStyle():
	return 'a' + str(random.randint(1, 5))

def processCommentNum(num):
	if num==1:
		return '1 Comment'
	else:
		return '{0} Comments'.format(num)

class Article:
	def __init__(self, args):
		self.articleURL = args[0]
		self.title = args[2]
		self.commentURL = args[1]
		self.tag = args[3].split(',')
		self.comments = processCommentNum(args[4])
		self.style = ['a1','a2','a3','a4','a5'][args[5]]

class Comment:
	def __init__(self, args):
		self.user = args[0]
		self.text = args[1]
		self.style = ['a1','a2','a3','a4','a5'][args[2]]