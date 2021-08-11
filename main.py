# -*- coding: UTF-8 -*-
# The Softwave to Make .uc file into song file
# Author : Cngmg，2021, Zhejiang
# Version : 1.0.0

from item import *
import argparse, os, sys, time

def main():
	parser = argparse.ArgumentParser(
		description='''Softwave - uc2mp3\nCreated By Cngmg'''
		)
	group = parser.add_mutually_exclusive_group()
	group.add_argument(
		"-s", "--single",
		help = "单文件转化，指向文件地址",
		required = False
		)
	group.add_argument(
		"-m", "--multiple",
		help = "多文件转化，指向文件夹地址",
		required = False
		)
	parser.add_argument(
		"-o", "--output",
		help = "输出文件夹",
		required = False,
		default = ".\\"
		)
	parser.add_argument(
		"-c", "--core",
		help = "运行核心数",
		required = False,
		type=int,
		default = 2
		)
	parser.add_argument(
		"-v", "--version",
		help = "版本号",
		action="version",
		version='main 1.0.0\nitem 1.3.0'
		)
	args = parser.parse_args()
	if args.single or args.multiple:
		strat_time = time.time()
		outpath = args.output
		if args.single:
			try:
				ErrCode = cache2song(args.single, outpath)
				if ErrCode != 0 :
					if ErrCode == 1:
						show_log("main : {State : Retry, Use Time : %s, Show Error : %s}"%(str(time.time() - strat_time),"Can't find .uc file"))
					elif ErrCode == 2:
						show_log("main : {State : Retry, Use Time : %s, Show Error : %s}"%(str(time.time() - strat_time),"Not a effective cache file"))
					else:
						show_log("main : {State : Retry, Use Time : %s, Show Error : %s}"%(str(time.time() - strat_time),"Can't find song's name and get singer name Or Can't connected to the Internet"))
					try:
						cache2song_without_info(args.single, outpath)
						show_log("main : {State : Success, Use Time : %s}"%str(time.time() - strat_time))
					except:
						show_log("main : {State : Break, Use Time : %s, Show Error : %s}"%(str(time.time() - strat_time),"Can't deal with The Error File."))
				else:
					show_log("main : {State : Success, Use Time : %s}"%str(time.time() - strat_time))
			except:
				try:
					show_log("main : {State : Retry, Use Time : %s, Show Error : %s}"%(str(time.time() - strat_time),"No info file"))
					cache2song_without_info(args.single, outpath)
					show_log("main : {State : Success, Use Time : %s}"%str(time.time() - strat_time))
				except:
					show_log("main : {State : Success, Use Time : %s}"%str(time.time() - strat_time))
		else:
			batchC2S(args.multiple, outpath, args.core)
		input("\nRun Success!\nPress Any Key to Exit.")
	else:
		os.system("%s -h"%sys.argv[0])
		input("\nPress Any Key to Exit.")

if __name__ == '__main__':
	main()