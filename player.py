
class player:
	def __init__(self,name,points_scored,points_lost,won,lost):
		self.name = name
		self.won = won
		self.lost = lost
		self.points_scored = points_scored
		self.points_lost = points_lost
		self.prev = None
		self.next = None


if __name__=='__main__':
	obj = player('gaurav',2,2,2,45,10)	#testing1
	print obj.points_lost				#testing2