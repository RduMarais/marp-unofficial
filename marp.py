import sublime
import sublime_plugin
from html.entities import html5
import configparser
import subprocess
import threading
import json


# with open('config.json', 'r') as config_file:
#     config_data = json.load(config_file)


history_filename = 'marp.sublime-settings'
config = sublime.load_settings(history_filename)


# config.set('chrome_path','test')
# CHROME_PATH = config.get('chrome_path')
# THEME_LIST = config.get('theme_list')


# TODO : https://docs.sublimetext.io/reference/commands.html#commands

class MarpBuild(threading.Thread):
	def __init__(self,file,theme,filetype):
		self.stdout = None
		self.stderr = None
		self.filename = file
		self.filetype = filetype
		self.css_file = config.get('theme_list').get(theme)['path']
		self.evt = evt
		threading.Thread.__init__(self)

	def print_output(self):
		self.stdout, self.stderr = self.build_process.communicate()
		print('[marp] output : ')
		print(self.stdout.decode("utf-8"))
		print(self.stderr.decode("utf-8"))

	def run(self):
		command = 'CHROME_PATH="'+config.get('chrome_path')+'" marp -o '+self.filename+'.'+self.filetype+' --allow-local-files --theme '+self.css_file+' '+self.filename
		print(command)

		if(self.filetype == 'pdf'):
			self.build_process = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
			print('[marp] done')
			self.print_output()

		if(self.filetype == 'html'):
			self.build_process = subprocess.Popen(command, shell = True, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
			self.evt.wait()
			self.build_process.kill()
			print('[marp] done')
			self.print_output()

	def stop(self):
		print('stopping')
		self.build_process.terminate()
		print('[marp] stopped')
		self.print_output()

class ThemeInputHandler(sublime_plugin.ListInputHandler):
	def list_items(self):
		return sorted(config.get('theme_list').keys())
	
	def placeholder(self):
		return "Name of build"
	
	# pour une string dynamique en dessous
	def preview(self, value):
		return "Build theme: {}".format(config.get('theme_list').get(value)['description'])

class MarppdfCommand(sublime_plugin.WindowCommand):
	def run(self,theme):
		filename = self.window.active_view().file_name()
		print('[marp] Build PDF document '+filename+' with theme : '+theme)
		build = MarpBuild(filename,theme,filetype='pdf')
		build.start()


	def input(self, args):
		return ThemeInputHandler()

class marploadCommand(sublime_plugin.WindowCommand):

	def run(self):
		print('[marp] load JSON file')
		view = self.window.active_view()
		filename = view.file_name()
		with open(filename, 'r') as config_file:
			try:
				config_data = json.load(config_file)
				print('[marp] json :\n'+str(config_data))
				for item in config_data:
					# print('[marp] type value :\n'+str(type(config_data[item])))
					config.set(item,config_data[item])
					sublime.save_settings(history_filename)
			except Exception as e:
				print('[marp] bad json')
				raise e

class MarpTestCommand(sublime_plugin.WindowCommand):
	def run(self):
		print('CHROME_PATH :\n'+str(config.get('chrome_path')))
		print('THEME_LIST :\n'+str(config.get('theme_list')))

class MarpstarthtmlCommand(sublime_plugin.WindowCommand):


	def run(self,theme):
		# self.evt = evt check evt
		view = self.window.active_view()
		filename = view.file_name()
		print('[marp] Watch HTML document '+filename+' with theme : '+theme)
		self.build = MarpBuild(filename,theme,filetype='html -w')
		self.build.start()


	def input(self, args):
		return ThemeInputHandler()

class MarpstophtmlCommand(sublime_plugin.WindowCommand):
	def run(self):
		global evt
		evt.set()

evt = threading.Event()