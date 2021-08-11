# -*- coding: UTF-8 -*-
# The Item is apart of uc2song project
# Author : Cngmg，2021, Zhejiang
# Version : 1.3.0

'''
Readme : 
	makesure you song cache file is SAVED!
	Or you can also USE <NEXT SONG> action to save song cache file and cache info.
'''

import requests, json, os, re, threading, time

def show_log(log):
	localtime = "[%s] : "%str(time.asctime(time.localtime(time.time())))
	open("log.log","a").write(localtime+log+"\n\n")
	print(log)

def get_mp3info(music_id): # 获取MP3文件名和歌手
	try:
		url = 'https://api.imjad.cn/cloudmusic/'
		# 请求url例子：https://api.imjad.cn/cloudmusic/?type=detail&id=1347203552
		payload = {'type': 'detail', 'id': music_id}
		reqs = requests.get(url, params=payload)
		jsons = reqs.json()
		song_name = jsons['songs'][0]['name']
		singer = jsons['songs'][0]['ar'][0]['name']
		return (True, song_name, singer)
	except Exception as e:
		return (False, str(e), 0)

def get_cacheinfo(idxpath): # 获取缓存文件信息
	# 允许IDX、INFO、UC文件的输入
	if ".idx" in idxpath or ".info" in idxpath or ".uc" in idxpath and os.path.exists(idxpath):
		tmpname = os.path.basename(idxpath)
		basename = tmpname.replace("." + os.path.basename(idxpath).split(".")[-1], "")
		dirname = os.path.dirname(idxpath)
		jsons = json.loads(open(dirname+"\\"+basename+".idx","rb").read())
		# 名字就是注释
		size = int(jsons["size"])
		istrue = jsons["t"]
		idlist = jsons["zone"]
		# idlist = x(index) id(music_id)
		jsons = json.loads(open(dirname+"\\"+basename+".info","rb").read())
		suffix = jsons["format"]
		return (istrue, size, idlist, suffix)
	else:
		return (False, 0, [], "Unknown")

class ThreadPool(): # 线程池
	
	def __init__(self,threadlist=[],runnum=0):
		self.threadlist = threadlist
		self.runnum = runnum
		self.runlist = []
		if runnum > len(threadlist):
			self.runnum = len(threadlist)
	
	def run(self):
		index = self.runnum
		self.runlist = self.threadlist[:index]
		for i in self.runlist:
			i.daemon = True
			i.start()
		while True:
			marklist = self.check()
			if len(marklist) > 0:
				for i in marklist:
					if index >= len(self.threadlist): break
					self.runlist[i] = self.threadlist[index]
					self.runlist[i].daemon = True
					self.runlist[i].start()
					index += 1
			if index >= len(self.threadlist) and len(self.check()) == self.runnum:
				break
			time.sleep(0.05)
	
	def check(self):
		index = []
		for i in range(len(self.runlist)):
			if not self.runlist[i].isAlive():
				index.append(i)
		return index
	
	def reset(self, threadlist, runnum):
		self.threadlist = threadlist
		self.runnum = runnum
		self.runlist.clear()

def cache2song(uc_path, outdir=".\\"): # 转化文件
	# Check the file
	def format_path(inputs):
		return "".join(re.findall(r'[^\*"/:?\\|<>]', inputs, re.S))
	if os.path.exists(uc_path) and os.path.isfile(uc_path):
		uc_content = open(uc_path,"rb").read()
		mp3_content = bytearray()
		for byte in uc_content:
			byte ^= 0xa3
			mp3_content.append(byte)
		istrue, size, idlist, suffix = get_cacheinfo(uc_path)
		if istrue and len(mp3_content) == size:
			music_id = idlist[0].split(" ")[-1]
			check, song_name, singer = get_mp3info(music_id) 
			if check:
				Output_name = "%s - %s.%s" % (format_path(singer), format_path(song_name), suffix)
				open(outdir + Output_name, "wb").write(mp3_content)
				return 0 # Success
			else:
				return 3 # Err3 - Can't find song's name and get singer name Or Can't connected to the Internet
		else:
			return 2 # Err2 - Not a effective file
	else:
		return 1 # Err1 - Can't find file

class cache2songThread(threading.Thread): # 转化线程

	def __init__(self, uc_path, outdir, index):
		threading.Thread.__init__(self)
		# When program exits, the thread automatically shut down
		self.daemon = True
		self.uc_path = uc_path
		self.outdir = outdir
		self.ErrCode = None
		self.index = index

	def run(self):
		strat_time = time.time()
		show_log("Thread-%d : {State : Run, Start Time : %s}"%(self.index,str(strat_time)))
		try:
			self.ErrCode = cache2song(self.uc_path, self.outdir)
		except:
			show_log("Thread-%d : {State : Retry, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"No info file"))
			cache2song_without_info(self.uc_path, self.outdir)
		if self.ErrCode == 1:
			show_log("Thread-%d : {State : Break, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"Can't find .uc file"))
		elif self.ErrCode == 2:
			try:
				show_log("Thread-%d : {State : Retry, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"Not a effective cache file"))
				cache2song_without_info(self.uc_path, self.outdir)
			except:
				show_log("Thread-%d : {State : Break, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"Can't deal with The Error File."))
		elif self.ErrCode == 3:
			try:
				show_log("Thread-%d : {State : Retry, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"Can't find song's name and get singer name Or Can't connected to the Internet"))
				cache2song_without_info(self.uc_path, self.outdir)
			except:
				show_log("Thread-%d : {State : Break, Use Time : %s, Show Error : %s}"%(self.index,str(time.time() - strat_time),"Can't deal with The Error File."))
		else:
			show_log("Thread-%d : {State : Success, Use Time : %s}"%(self.index,str(time.time() - strat_time)))

def batchC2S(dirpath, outdir=".\\", core_num=2): # 批量转化
	# core_num为你的电脑的核心数，决定了允许的最大线程数，为core_num+1
	# core_num is the core number of CPU, the Max Thread number is determinesed by core.
	# Check the path
	if os.path.exists(dirpath) and not os.path.isfile(dirpath):
		dirrange = os.listdir(dirpath)
		thread_range = []
		index = 0
		for i in dirrange:
			if ".uc" == i[-3:]:
				thread_range.append(cache2songThread(dirpath + "\\" + i, outdir, index))
				index += 1
		ThreadPool(thread_range, core_num+1).run()
		return True
	else:
		return False # Can't find the dir

def cache2song_without_info(uc_path, outdir=".\\"):
	if os.path.exists(uc_path) and os.path.isfile(uc_path):
		uc_content = open(uc_path,"rb").read()
		mp3_content = bytearray()
		for byte in uc_content:
			byte ^= 0xa3
			mp3_content.append(byte)
		Output_name = outdir + os.path.basename(uc_path)[:-3]+"_noinfo.mp3"
		open(outdir + Output_name, "wb").write(mp3_content)
		return True
	else:
		return False

if __name__ == '__main__':
	print("This is a Item file!Please Use the main.py!")
	# Test
	print(batchC2S(r"E:\CloudMusic\Cache\Cache"))