def get_type(line):
	field_name = line.split(":")[0]
	if len(line.split(":")) > 1:
		#print "Have value"
		return len(line.split(":"))
	else:
		#print "Have one value"
		return 1

	return None

def get_field(line):
	
	if len(line.split("=")) > 1:

		if len(line.split("=")[1].split(" - ")) > 1:
			return line.split("=")[1].split(" - ")[0].strip()
		else:
			return line.split("=")[1].strip().split(":")[0].strip()

	else:
		if ".." in line.split(":")[0].strip():
			# print (line.split(":")[0].split(" ")[-1])
			# exit()
			return line.split(":")[0].split(" ")[-1]

		return line.split(":")[0].strip()
		

		#  .1.. .... = 128-EEA1: Supported
		#  ..0. .... = Indicator 43: Undefined - Not supported



def get_value(line):
	
	if len(line.split("=")) > 1:

		if len(line.split("=")[1].split(" - ")) > 1:
			return line.split("=")[1].split(" - ")[1].strip()
		else:
			return line.split("=")[1].strip().split(":")[1].strip()

	return line.split(":")[1].strip()
		

# --------------------------------------------------------
# Functions for Handling Trees
# --------------------------------------------------------
class Node:
	def __init__(self,nodenum,isleaf,featurenum,criteria,devices):
		self.nodenum=nodenum
		self.isleaf=isleaf
		self.featurenum=featurenum
		self.criteria=criteria
		self.devices=devices
		
		self.right=None
		self.left=None
		self.parent=None
		
	def set_right(self,right):
		self.right=right
	
	def set_left(self,left):
		self.left=left

	def add_device(self,num):
		self.devices.append(num)

	def insert(self,node):
		if self.left==None:
			self.left=node
		else :
			if self.right!=None:
				print("Error : left and right are all full already")
			else :
				self.right=node
	
	def left_or_right(self):
		# -1 : left, 0 : error, 1: right
		if self.parent==None:
			print("Possibly error")
			return 0
		else :
			if self.parent.left.nodenum==self.nodenum:
				return -1
			elif self.parent.right.nodenum==self.nodenum :
				return 1
	
def parse_line(line):
	line_node=1
	# if line_node<0 : 2->3 line
	# if not, node description line
	# exceptions : first 2 and last line -> line_node=0
	try :
		line.index('->')
		line_node=-1
		startnum=line[:line.index('-')-1]
		cutline=line[line.index('>')+2:]
		endnum=cutline[:cutline.index(' ')]
		
		return [line_node,startnum,endnum]
	
	except :
		if '}' in line:
			return [0]
		elif 'digraph' in line:
			return [0]
		elif 'node' in line:
			return [0]
		elif 'edge' in line:
			return [0]

		isleaf=0
		nodenum=int(line[:line.index(' ')])
		point=line.index('"')
		# print (line)
		# print (point)
		if line[point+1:point+11]=="samples = ":
			featurenum=-1
			isleaf=-1
		else :
			featurenum=line[line.index('"')+1:line.index("<")-1]

		if isleaf==0:
			criteria=float(line[line.index('<=')+3:line.index('samples')-2])
		else :
			criteria=-1
		
		list_devices=line[line.index('value =')+9:line.index(']')].replace('\\n',', ').split(',')
		temp_list=[]
		for i in list_devices:
			# print(i)
			try :
				temp_list.append(int(i))
			except :
				pass
		# print (temp_list)
		devices=handle_list_devices(temp_list)

		return [line_node,nodenum,isleaf,featurenum,criteria,devices]

def handle_list_devices(device_list):
	devices=[]    
	for i in range(len(device_list)):
		if int(device_list[i])>=1:
			devices.append(i)
	if devices==[]:
		print("Possibly error : no device in the node")
	return devices
