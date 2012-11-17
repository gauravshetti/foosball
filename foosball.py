import os
import pickle,re
from player import player
from time import sleep

class foosball:
	'''
	Constructor, which loads the data fro the rankingsFile and creates a dict for searching and linkedList for maintaining 
	the ranking structure.
	'''
	def __init__(self,directory,rankingsFile):
		if not os.path.exists(directory):
			os.makedirs(directory)
		self.rfile = os.path.join(directory,rankingsFile)
		self.reset()
		if os.path.exists(self.rfile):	#if file doesn't exist, do nothing.
			pkl_file = open(self.rfile,'rb')
			self.rankingsDict = pickle.load(pkl_file)	#the ranking is stored in form of a list
			if len(self.rankingsDict) > 0:
				self.firstNode = self.rankingsDict[0]
				total_length = len(self.rankingsDict)
				for i in range(0, total_length):
					obj = self.rankingsDict[i]
					self.playersDict[obj.name] = obj
					obj.next = self.rankingsDict[i+1] if i!=total_length-1 else None
					obj.prev = self.rankingsDict[i-1] if i!=0 else None
				self.lastNode = self.rankingsDict[total_length-1]
			pkl_file.close()

	'''
	initialize the data
	'''
	def reset(self):
		self.rankingsDict = []
		self.firstNode = None
		self.lastNode = None
		self.playersDict = {}

	'''
	the main controller to process the data for each match which is in the format
	player,score,player,score
	'''
	def updateRankings(self,data):
		data = data.split(",")
		try:
			data[1] = int(data[1])	#playar1 score
			data[3] = int(data[3])	#player2 score
			if data[1] > data[3]:
				self.processInfo(data[0],data[1],data[3],1)
				self.processInfo(data[2],data[3],data[1],0)
			else:
				self.processInfo(data[0],data[1],data[3],0)
				self.processInfo(data[2],data[3],data[1],1)
		except:		#if any error, we assume its the format of the input that is faltered
			print "invalid input: " + str(data) +"\n"

	
	'''
	splitting in terms of creating a new node or updating the existing node
	'''
	def processInfo(self,name,points_scored,points_lost,result):
		obj = self.playersDict[name] if name in self.playersDict else None
		if obj != None:
			self.update(obj,points_scored,points_lost,int(result))
		else:
			self.create(name,points_scored,points_lost,int(result))

	def create(self,name,points_scored,points_lost,result):
		obj = player(name,points_scored,points_lost,1,0) if result==1 else player(name,points_scored,points_lost,0,1)
		self.playersDict[name]=obj
		if self.firstNode == None:	#this is the first node to be inserted in the rankingsDict
			self.firstNode = obj
			self.lastNode = obj
		else:
			if result == 1:			#win/lost
				self.adjustnode(obj,self.lastNode,int(points_scored),int(points_lost),1,0)
			else:
				self.adjustnode(obj,self.lastNode,int(points_scored),int(points_lost),0,1)

	
	'''
	adjusting the node within the linkedlist
	'''
	def adjustnode(self, obj, fromNode,points_scored,points_lost,won,lost):
		node = fromNode		#the node to be compared with

		while (int(node.won) < won) or (int(node.won) == won and int(node.points_scored)< points_scored) or \
		(int(node.won) == won and int(node.points_scored) == points_scored and int(node.points_lost) > points_lost) or \
		(int(node.won) == won and int(node.points_scored) == points_scored and int(node.points_lost) == points_lost and int(node.lost) > lost):
			node = node.prev
			if node == None:
				break
		#if not the first node, set the approporiate pointers
		if node != None:
			if node.next == None:	#if new node is to be put at the last, change the lastnode pointer
				self.lastNode = obj 
			obj.next = node.next
			node.next = obj
			obj.prev = node
			if obj.next != None:	#if new node is to be inserted between 2 nodes, get the prev pointer pointed correctly
				(obj.next).prev = obj
		else:	#set the new object as the first node
			obj.prev = None
			obj.next = self.firstNode
			self.firstNode.prev = obj
			self.firstNode = obj

	
	'''
	for updating, we delete the node from the current position and readjust its position
	'''
	def update(self,obj,points_scored,points_lost,result):
		obj.points_scored = int(obj.points_scored) + int(points_scored)
		obj.points_lost = int(obj.points_lost) + int(points_lost)
		if result == 0:
			obj.lost = int(obj.lost) + 1
		else:
			obj.won = int(obj.won) + 1
		if obj.prev != None:	#if already rank1 , then do not adjust
			(obj.prev).next = obj.next
			if (obj.next) != None:
				(obj.next).prev = obj.prev
			self.adjustnode(obj,obj.prev, int(obj.points_scored), int(obj.points_lost), int(obj.won), int(obj.lost))

	'''
	if you need to see top n rankings, pass an integer value of >1 in top.
	Else pass 0
	'''
	def showRankings(self,top):
		top = int(top)
		if len(self.playersDict) == 0:
			print "no data\n"
		else:
			if top < 0:
				top = 0
			node = self.firstNode
			rank = 1
			while((not(top) and node!=None) or ((top) and (rank <= top) and node!=None)):
				if rank == 1:
					print ".*.# Current Leader #.*."
				else:
					print "rank : " + str(rank)
				print node.name
				print "won : "+ str(node.won) +" lost: "+str(node.lost)
				print "points scored: "+ str(node.points_scored) +" points lost: "+ str(node.points_lost) +"\n"
				node = node.next
				rank = rank + 1

	'''
	 specify the filename of the file from where results needs to be uploaded
	'''
	def bulkupload(self,filename):
		f = open(filename, 'r+')
		for line in f:
			self.updateRankings(line)
		f.close()
		print "Completed processing of the file\n"


	'''
	simple header structure
	'''
	def header(self):
		print "**** Foosball application ****"
		print "   designed by Gaurav Shetti  "
		print "-------------------------------\n"


	'''
	save the file to the original file from where results were loaded
	'''
	def saveFile(self):
		if len(self.playersDict) > 0:
			node = self.firstNode
			temp = []
			for i in range(0,len(self.playersDict)):
				temp.append(node)
				node = node.next
				print i
			output_pkl_file = open(self.rfile, 'wb')
			pickle.dump(temp,output_pkl_file)
			output_pkl_file.close()
			print "File saved into : "+ self.rfile +"\n"
		else:
			print "No data for to be saved \n"

	def passwordProt(self):
		input_data3=raw_input("Enter the password to enter the data :")
		if input_data3 == "password123":
			return True
		else:
			return False

	def deletematch(self,match):
			data = match.split(",")
		
			data[1] = int(data[1])	#player1 score
			data[3] = int(data[3])	#player2 score
			if data[1] > data[3]:
				self.deleteInfo(data[0],data[1],data[3],1)
				self.deleteInfo(data[2],data[3],data[1],0)
			else:
				self.deleteInfo(data[0],data[1],data[3],0)
				self.deleteInfo(data[2],data[3],data[1],1)

	def deleteInfo(self,name,points_scored,points_lost,result):
		obj = self.playersDict[name] if name in self.playersDict else None
		if obj != None:
			self.delete(obj,points_scored,points_lost,int(result))

	def delete(self,obj,points_scored,points_lost,result):
		obj.points_scored = int(obj.points_scored) - int(points_scored)
		obj.points_lost = int(obj.points_lost) - int(points_lost)
		if result == 0:
			obj.lost = int(obj.lost) - 1
		else:
			obj.won = int(obj.won) - 1

		if (obj.won == 0 and obj.lost == 0):
			if obj.prev!=None:
				obj.lastNode = obj.prev
				(obj.prev).next = None
		else:
			if obj.next != None:
				self.del_adjustnode(obj,obj.next,int(obj.points_scored), int(obj.points_lost), int(obj.won), int(obj.lost))

	def del_adjustnode(self, obj, fromNode,points_scored,points_lost,won,lost):
		node = fromNode		#the node to be compared with

		while (int(node.won) > won) or (int(node.won) == won and int(node.points_scored)> points_scored) or \
		(int(node.won) == won and int(node.points_scored) == points_scored and int(node.points_lost) < points_lost) or \
		(int(node.won) == won and int(node.points_scored) == points_scored and int(node.points_lost) == points_lost and int(node.lost) < lost):
			node = node.next
			if node == None:
				break
		#if not the last node, set the approporiate pointers
		if node != None:
			if node.next == None:	#if new node is to be put at the last, change the lastnode pointer
				self.lastNode = obj 
			obj.prev = node.prev
			node.prev = obj
			obj.next= node
		else:	#set the new object as the first node
			obj.next = None
			obj.prev = self.lastNode
			self.lastNode.next = obj
			self.lastNode = obj

if __name__=='__main__':
	obj = foosball('files','rankingData')
	
	#testing
	'''obj.updateRankings('Diego,5,Amos,4')
	obj.updateRankings('Amos,1,Diego,5')
	obj.updateRankings('Amos,2,Diego,5')
	obj.updateRankings('Amos,0,Diego,5')
	obj.updateRankings('Amos,6,Diego,5')
	obj.updateRankings('Amos,5,Diego,2')
	obj.updateRankings('Amos,4,Diego,0')
	obj.updateRankings('Joel,4,Diego,5')
	obj.updateRankings('Tim,4,Amos,5')
	obj.updateRankings('Tim,5,Amos,2')
	obj.updateRankings('Amos,3,Tim,5')
	obj.updateRankings('Amos,5,Tim,3')
	obj.updateRankings('Amos,5,Joel,4')
	obj.updateRankings('Joel,5,Tim,2')'''
	#obj.showRankings()
	obj.header()
	while(True):
		print "Press 1 to bulk upload historical data"
		print "Press 2 to enter a single record"
		print "Press 3 to view the current rankings"
		print "Press 4 to save the data"
		print "Press 5 to delete the data"
		print "Else press q to quit"
		input_data = raw_input("\nEnter a choice: ")
		if input_data.lower() == 'q':
			break
		elif input_data == "1":
			try:
				if (obj.passwordProt()):
					input_data2 = raw_input("Enter the filename with proper directory structure if applicable: ")
					obj.bulkupload(input_data2)
					obj.showRankings(10)
				else:
					print "Not sufficient privileges to enter the data"
			except:
				print "Invalid input\n"
		elif input_data == "2":
			if (obj.passwordProt()):
				input_data2 = raw_input("Enter the scores in the format : Player1,score1,player2,score2 :")
				obj.updateRankings(input_data2)
				print "\n Top 10 rankers"
				obj.showRankings(10)
			else:
				print "Not sufficient privileges to enter the data"
				
		elif input_data == "3":
			input_data2 = raw_input("Enter 0 to display all ranks or enter a number to display records till that numbers :")
			obj.showRankings(int(input_data2))
		elif input_data == "4":
			obj.saveFile()
		elif input_data == "5":
				input_data2 = raw_input("Enter the match data to be deleted :")
				obj.deletematch(input_data2)
				obj.showRankings(0)
		else:
			print "Enter a proper choice\n"


