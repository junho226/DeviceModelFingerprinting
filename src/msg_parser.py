import sys
import re
import logging
import argparse
from cStringIO import StringIO
from utils import get_type, get_field, get_value
from collections import OrderedDict
import pdb
import code
import os
import csv
# define constants
TAB_SIZE = 4

# global variable
logger = logging.getLogger('MSG_PARSER_LOG')
logger.setLevel(logging.ERROR)

print_avoid_list = [
# NAS IEs
'Protocol discriminator', 'Security header type', 'Attach request message identity', 'EPS attach type', 'NAS key set identifier', 'EPS mobile identity',
'ESM message container', 'Old P-TMSI signature', 'Additional GUTI', 'Last visited registered TAI', 'TMSI Status', 'Additional update type',
'Device properties', 'Old GUTI type', 'TMSI based NRI container', 'UE radio capability ID availability', 'UE status', 'Additional information requested',
'IMSI offset', 'Requested WUS assistance information', 'Old location area identification', "NAS EPS Mobility Management Message Type",
"ueCapabilityRAT-Container"

# RRC fields
,'skipSubframeProcessing','skipFallbackCombRequested','requestedDiffFallbackCombList','requestedBands','requestedCCsDL'
,'requestedCCsUL','FeatureSetDL-PerCC-Id','FeatureSetUL-PerCC-Id','wlan-MAC-Address'

# Processing (Included due to the implementation issue: Cannot exactly capture target messages)
,"ulInformationTransfer", "rrcConnectionReconfigurationComplete", "counterCheckResponse","ueInformationResponse-r9", "securityModeComplete", "securityModeFailure"

,"registeredMME", "gummei"
]
# , "nonContiguousUL-RA-WithinCC-List-r10"
# "gummei-Type-r10"
# print_avoid_list = [
# "nonContiguousUL-RA-WithinCC-List-r10",
# "ulInformationTransfer", "rrcConnectionReconfigurationComplete", "counterCheckResponse","ueInformationResponse-r9", "securityModeComplete", "EPS mobile identity", "securityModeFailure", 
# "Security header type", "NAS EPS Mobility Management Message Type", "NAS key set identifier",
# "Protocol discriminator", "EPS attach type","TMSI Status", "GUTI type - Old GUTI type", "Location area identification - Old location area identification",
# "Tracking area identity - Last visited registered TAI", "Protocol or Container ID", "registeredMME", 
# "Network Resource Identifier Container - TMSI based NRI container", "gummei-Type-r10", "EPS mobile identity - Additional GUTI"
# ]

rf_Parameters = ""

skip_field_list = [
"dedicatedInfoNAS", "Procedure transaction identity", "ueCapabilityRAT-Container", "featureGroupIndicators", "Message authentication code", "featureGroupIndicators-r9", "featureGroupIndRel9Add-r9",
"lateNonCriticalExtension", "Length", "c1", "criticalExtensions", "Element ID", "Spare bit(s)", "Bitmap Length", "Sequence number", "Identifier", "nonCriticalExtension", 'selectedPLMN-Identity'
]
# print_avoid_list = []
# skip_field_list = []

class MsgTree:
	""" Containing root information. """
	def __init__(self):
		self._child_list = OrderedDict()
		self._parent = None
		self._depth = 0
		# name of root (Field name)
		self._name = ""
		#  node ftype
		self._ftype = None
		# possible values
		self._values = list()

	# def __del__(self):
	# 	# print ("Tree is destoryed {}".format(self._name))


	def get_name(self):
		return self._name

	def find(self, line):
		if line in self._child_list:
			return self._child_list.get(line)
		return None

	def set_root(self, field_name, ftype, parent, depth):
		self._name = field_name
		self._parent = parent
		self._depth = depth
		self._ftype = ftype
		return

	def set_value(self, value):
		self._values.append(value)	
		return

	def get_parent(self):
		return self._parent

	def get_depth(self):
		return self._depth

	def add_child(self, child_tree, field_name):
		# field_name = line.split(":")[0]
		self._child_list[field_name] = child_tree
		return True

	def print_tree(self):
		space = "  " * self._depth
		if self._ftype == 2:
			if self._name not in skip_field_list:
				print ("{}{}: {}".format(space, self._name, self._values))
		else:
			if self._name not in skip_field_list:
				print ("{}{}: [Exist]".format(space, self._name))

		for key, child_item in self._child_list.items():
			flag = 0
			for element in print_avoid_list:
				if element in key :
					flag = 1
					break
			# if key not in print_avoid_list: 
			# 	child_item.print_tree()
			if flag == 0:
				child_item.print_tree()

	def print_tree_name_csv(self):
		space = "  " * self._depth
		if self._ftype == 2:
			if self._name not in skip_field_list:
				# print ("{}{}: {}".format(space, self._name, self._values))
				new_row.append(self._name)
		else:
			# print ("{}{}: [Exist]".format(space, self._name))
			if self._name not in skip_field_list:
				new_row.append(self._name)

		for key, child_item in self._child_list.items():
			flag = 0
			for element in print_avoid_list:
				if element in key :
					flag = 1
					break
			# if key not in print_avoid_list: 
			# 	child_item.print_tree_name_csv()
			if flag == 0:
				child_item.print_tree_name_csv()



class MsgParser:
	def __init__(self):
		self._node_counter = 0
		self.logger = logging.getLogger()
		self.filter_list = []
		self.tree = MsgTree()

	def set_filter(self, filter_str):
		self.filter_list.append(filter_str)
		return None

	def set_logger(self, clogger):
		self.logger = clogger
		return None

	def parse_msg(self, msg):
		""" Parse the given RRC message. """

		# rewind the IO buffer
		msg.seek(0)

		# skip first line and second line
		msg.readline()
		msg_ftype = msg.readline().strip()
		self.logger.debug(msg_ftype)

		if msg_ftype not in self.filter_list:
			self.logger.debug(msg)
			self.logger.debug("Skip msg! Given: {}".format(msg_ftype))
			return

		# parse the given msg line by line
		cur_tree = self.tree
		cur_depth = 0
		is_skip = False
		skip_depth = 0

		# self.logger.debug(msg.getvalue())
		while True:
			line = msg.readline()
			if not line:
				break

			# calculate depth
			depth = (len(line) - len(line.lstrip(' '))) / TAB_SIZE - 1
			
			# extract field_name
			line = line.strip()

			field_name = get_field(line)
			ftype = get_type(line)
			
			if is_skip:
				if skip_depth < depth:
					self.logger.debug("SKIP depth: {}, field_name: {} ftype: {}".format(depth, field_name, ftype))		
					continue
				else:
					is_skip = False
					self.logger.debug("Skip finish")

			self.logger.debug("depth: {}, field_name: {} ftype: {}".format(depth, field_name, ftype))

			flag = 0
			for element in print_avoid_list:
				if element in field_name:
					flag = 1
					break

			if flag == 1:
				skip_depth = depth
				is_skip = True
				self.logger.debug("Start to skip")
			
			elif field_name.startswith("Item"):
				# print (cur_tree._name)
				# print (field_name)
				if (cur_tree._name != "ue-CapabilityRAT-ContainerList"):
					skip_depth = depth
					is_skip = True
					self.logger.debug("Start to skip")

			# extract value 
			if ftype > 1:
				value = line.split(":")[1].strip()
				value = get_value(line)
				self.logger.debug("line| {}".format(line))
				self.logger.debug("field_name: [{}] value: [{}]" .format(field_name, value))

			cur_depth = cur_tree.get_depth()

			if field_name in self.filter_list:
				self.logger.debug("Skip msg!")
				continue

			elif field_name.startswith("Item"):
				# print (cur_tree._name)
				# print (field_name)
				if (cur_tree._name != "ue-CapabilityRAT-ContainerList"):
					continue
			

			# find proper parent tree
			if depth > cur_depth:
				cur_tree
			elif depth == cur_depth:
				cur_tree = cur_tree.get_parent()
				cur_depth = cur_tree.get_depth()
			else:
				while depth <= cur_depth:
					cur_tree = cur_tree.get_parent()
					cur_depth = cur_tree.get_depth()
			self.logger.debug("cur_tree info: depth: {}, field_name: {} ftype: {}".format(cur_depth, cur_tree.get_name(), ftype))		


			# allocate child tree
			child_tree = cur_tree.find(field_name)

			if child_tree:
				# move the child (sub-tree)
				cur_tree = child_tree
				# TODO need to add values
				if value not in cur_tree._values:
					cur_tree._values.append(value)		
					self.logger.debug("ADD value")
					self.logger.debug("Tree value: {}".format(cur_tree._values))

			else:
				# allocate new child
				new_child = MsgTree()
				new_child.set_root(field_name, ftype, cur_tree, depth)
				if (ftype > 1):
					new_child.set_value(value)
				cur_tree.add_child(new_child, field_name)

				# move to the child sub-tree
				cur_tree = new_child
						


def __log_settings():
	file_handler = logging.FileHandler('./msg_parser.log', mode='w')
	stream_handler = logging.StreamHandler()

	file_handler.setLevel(logging.DEBUG)
	stream_handler.setLevel(logging.INFO)

	formatter = logging.Formatter(
		'[%(levelname)s][%(filename)s:%(lineno)s]> %(message)s')
	file_handler.setFormatter(formatter)
	stream_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)

	
def write_tree_csv(parser_tree, sep_parser_tree):
	
	if (sep_parser_tree):
		# print ("Wrong")

		if parser_tree._ftype == 2:
			if parser_tree._name not in skip_field_list:
				# print ("{}{}: {}".format(space, self._name, self._values))
				if (sep_parser_tree._values):
					new_row.append(sep_parser_tree._values)
					
					r_new_row.append(parser_tree._values.index(sep_parser_tree._values[0]))
					

				else:
					new_row.append("None")
					r_new_row.append("-1")
		else:
			# print ("{}{}: [Exist]".format(space, self._name))
			if parser_tree._name not in skip_field_list:
				new_row.append("[Exist]")
				r_new_row.append("1")

	else:
		if parser_tree._ftype == 2:
			if parser_tree._name not in skip_field_list:
				# print ("{}{}: {}".format(space, self._name, self._values))
				new_row.append("None")
				r_new_row.append("-1")
		else:
			# print ("{}{}: [Exist]".format(space, self._name))
			if parser_tree._name not in skip_field_list:
				new_row.append("None")
				r_new_row.append("-1")
		


	if (sep_parser_tree):
		for key, child_item in parser_tree._child_list.items():
			flag = 0
			for element in print_avoid_list:
				if element in key:
					flag = 1
					break

			if flag == 0:
				if key in sep_parser_tree._child_list.keys(): 
					write_tree_csv(child_item, sep_parser_tree._child_list[key])
				else:
					write_tree_csv(child_item, None)

	else:
		for key, child_item in parser_tree._child_list.items():
			flag = 0
			for element in print_avoid_list:
				if element in key:
					flag = 1
					break

			if flag == 0:
				write_tree_csv(child_item, None)
	return


if __name__ == '__main__':
	
	# init variables
	isRRC = False
	parser = MsgParser()
	parser.set_filter("UL-DCCH-Message")
	# parser.set_filter("ueCapabilityInformation")

	# logging setting
	__log_settings()
	parser.set_logger(logger)

	# argument checking
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-f", "--file", help="Pcap(text format) file name")
	argparser.add_argument("-d", "--dir", help="Pcap(text format) dir file name")
	argparser.add_argument("-s", "--save", help="save to csv file")
	args = argparser.parse_args()

	if (args.file):
		in_filename = args.file
		logger.info("inputfilename: " + str(in_filename))

		in_filename_t = in_filename
		f = open(in_filename_t, 'rb')
		while True:
			inputline = f.readline()
			if not inputline:
				break

			# find starting point RRC message part
			if not (inputline.startswith('                ') or inputline.startswith('\t')):
				# parser.logger.debug(inputline)
				# print (inputline)
				# Assumption: RRC message start with following string
				if "LTE Radio Resource Control (RRC) protocol" in inputline:
					isRRC = True
					parser.logger.debug(inputline)
					# generate new RRC MSG
					rrc_msg = StringIO()
					rrc_msg.write(inputline)

				else:
					if isRRC:
						# RRC msg is ended
						msg_str = rrc_msg.getvalue()
						# parser.logger.debug(msg_str)
						isRRC = False

						parser.parse_msg(rrc_msg)

			elif isRRC:
				# append msg
				rrc_msg.write(inputline)
      
			f.close

	else:
		# directory check
		print("Read logs from the given dir: " + str(args.dir))

		dirname = args.dir.split('/')[-1]
		print(dirname)

		STORAGE = "fl_" + dirname + "rrctest.csv"
		csv_f = open(STORAGE, "w")
		csv_wr = csv.writer(csv_f)
		new_row = list()

		STORAGE_2 = "flr_" + dirname + "rrctest.csv"
		r_csv_f = open(STORAGE_2, "w")
		r_csv_wr = csv.writer(r_csv_f)
		r_new_row = list()

		file_list = os.listdir(dirname) 
		print(file_list)
	
		if os.path.isdir(dirname):
			file_list = os.listdir(dirname)
			file_list.sort()
			print (file_list)
		else:
			print("given dir is not directory name!: " + str(dirname))
			sys.exit()

		for file_name in file_list:
			full_filename = dirname+"/"+file_name
			# os.path.join(full_dirname + file_name)
			# print("Currnet file: " + full_filename)
			
			if full_filename.endswith(".txt"):
				# print("Process")		

				in_filename_t = full_filename

				f = open(in_filename_t, 'rb')
				while True:
					inputline = f.readline()
					if not inputline:
						break

					# find starting point RRC message part
					if not (inputline.startswith('                ') or inputline.startswith('\t')):
						# parser.logger.debug(inputline)
						# print (inputline)
						# Assumption: RRC message start with following string
						if "LTE Radio Resource Control (RRC) protocol" in inputline:
							isRRC = True
							parser.logger.debug(inputline)
							# generate new RRC MSG
							rrc_msg = StringIO()
							rrc_msg.write(inputline)

						else:
							if isRRC:
								# RRC msg is ended
								msg_str = rrc_msg.getvalue()
								# parser.logger.debug(msg_str)
								isRRC = False

								parser.parse_msg(rrc_msg)

					elif isRRC:
						# append msg
						rrc_msg.write(inputline)
					
					f.close

		new_row = list()
		new_row.append("device")
		parser.tree.print_tree_name_csv()
		csv_wr.writerow(new_row)
		r_csv_wr.writerow(new_row)

		for file_name in file_list:
			full_filename = dirname+"/"+file_name
			# os.path.join(full_dirname + file_name)
			# print("Currnet file: " + full_filename)
			
			if full_filename.endswith(".txt"):
				# print("Process")		


				sep_parser = MsgParser()
				sep_parser.set_filter("UL-DCCH-Message")
				# parser.set_filter("ueCapabilityInformation")

				# logging setting
				__log_settings()
				sep_parser.set_logger(logger)

				in_filename_t = full_filename

				f = open(in_filename_t, 'rb')
				while True:
					inputline = f.readline()
					if not inputline:
						break

					# find starting point RRC message part
					if not (inputline.startswith('                ') or inputline.startswith('\t')):
						# parser.logger.debug(inputline)
						# print (inputline)
						# Assumption: RRC message start with following string
						if "LTE Radio Resource Control (RRC) protocol" in inputline:
							isRRC = True
							sep_parser.logger.debug(inputline)
							# generate new RRC MSG
							rrc_msg = StringIO()
							rrc_msg.write(inputline)

						else:
							if isRRC:
								# RRC msg is ended
								msg_str = rrc_msg.getvalue()
								# sep_parser.logger.debug(msg_str)
								isRRC = False

								sep_parser.parse_msg(rrc_msg)

					elif isRRC:
						# append msg
						rrc_msg.write(inputline)

				new_row = list()
				new_row.append(in_filename_t)

				r_new_row = list()
				r_new_row.append(in_filename_t)

				write_tree_csv(parser.tree, sep_parser.tree)
				csv_wr.writerow(new_row)

				# fingerprint = '/'.join(map(str, r_new_row[1:]))
				# print(fingerprint)
				# r_new_row.append(fingerprint)
				r_csv_wr.writerow(r_new_row)

				# print (new_row)
			
				f.close

	print ("finish")
	parser.tree.print_tree()

	
	# code.interact(local=locals())
	# print (parser.tree._values.keys())