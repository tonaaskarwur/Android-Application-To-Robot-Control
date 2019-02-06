import socket
import time
import GlobalShared
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from plyer import accelerometer
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex as rgb
from kivy.garden.graph import Graph, LinePlot
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.logger import Logger
import sqlite3
import pickle

try:
	from jnius import autoclass
	from android.runnable import run_on_ui_thread

	android_api_version = autoclass('android.os.Build$VERSION')
	AndroidView = autoclass('android.view.View')
	AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

	Logger.debug(
		'Application runs on Android, API level {0}'.format(
			android_api_version.SDK_INT
		)
	)
except ImportError:
	def run_on_ui_thread(func):
		def wrapper(*args):
			Logger.debug('{0} called on non android platform'.format(
				func.__name__
			))
		return wrapper

Builder.load_file('App_Kivy.kv')

class MenuImageButton(ButtonBehavior, Image):  
	def on_press(self):
		self.source = 'Img/button_dn.png'

	def on_release(self):
		self.source = 'Img/button.png'

class ArrowImageButton(ButtonBehavior, Image):  
	def on_press(self):
		self.source = 'Img/back_arrow_dn.png'

	def on_release(self):
		self.source = 'Img/back_arrow.png'

class WifiImageButton(ButtonBehavior, Image):
	def on_press(self):
		self.source = 'Img/wifi_dn.png'

	def on_release(self):
		self.source = 'Img/wifi.png'

class DatabaseImageButton(ButtonBehavior, Image):
	def on_press(self):
		self.source = 'Img/database_dn.png'

	def on_release(self):
		self.source = 'Img/database.png'

class GoImageButton(ButtonBehavior, Image):
	def on_press(self):
		self.source = 'Img/go_dn.png'

	def on_release(self):
		self.source = 'Img/go.png'

class MenuScreen(Screen):

	def __init__(self, **kwargs):

		super(Screen,self).__init__(**kwargs)
		self.box = BoxLayout(orientation = 'vertical')

		self.host_input = TextInput(id='host', text=GlobalShared.host, font_size=25, multiline=False)
		self.box.add_widget(self.host_input)
		self.port_input = TextInput(id='port', text=str(GlobalShared.port), font_size=25, multiline=False)
		self.box.add_widget(self.port_input)
		self.box.add_widget(Button(text='OK', on_press = lambda a:self.try_connect()))
		
		self.popup = Popup(title='Set IP and HOST', auto_dismiss=False, size_hint=(.5, .5), content = self.box)

		self.tick = Image(id= 'tick', source='Img/tick.png',
				allow_stretch= False,
				keep_ratio= True,
				pos_hint= {"center_x": 0.73, "center_y": 0.8},
					size_hint= (0.08, 0.08))

		self.wrong = Image(id= 'wrong', source='Img/wrong.png',
				allow_stretch= False,
				keep_ratio= True,
				pos_hint= {"center_x": 0.73, "center_y": 0.8},
					size_hint= (0.08, 0.08))

	@run_on_ui_thread
	def android_set_hide_menu(self):
		if android_api_version.SDK_INT >= 19:
			Logger.debug('API >= 19. Set hide menu')
			view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
			view.setSystemUiVisibility(
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
				AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
				AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
				AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
				)
	
	def check_wifi_status(self):
		if GlobalShared.error == True:
			self.remove_widget(self.tick)
			self.remove_widget(self.wrong)
			self.add_widget(self.wrong)
			GlobalShared.error = False

	def change_host_and_ip(self, host, port):
		#Change host and ip
		GlobalShared.host = host
		GlobalShared.port = int(port)

	def try_connect(self):
		self.change_host_and_ip(self.host_input.text, self.port_input.text)
		self.wifi_active()
		self.popup.dismiss()
		self.android_set_hide_menu()

	def open_popup(self):
		self.popup.open()
		
	#When hit wigfi image
	def wifi_active(self):
		#Try connect
		
		#Clear error conection label
		global s
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(1)   # 1 seconds
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		adress = ((GlobalShared.host, GlobalShared.port))
		try:
			s.connect(adress)
			answer = s.recv(2)
			if answer == b'GC':
				self.remove_widget(self.tick)
				self.remove_widget(self.wrong)
				self.add_widget(self.tick)
				GlobalShared.wifi = True

		except socket.error:
			self.remove_widget(self.wrong)
			self.remove_widget(self.tick)
			self.add_widget(self.wrong)
			GlobalShared.wifi = False


	def exit_app(self):
		if GlobalShared.wifi == True:
			#s.send(str.encode('EX'))
			s.close()
		App.get_running_app().stop()

	def open_button(self):
		self.add_widget(self.ids.button_dn)
		self.remove_widget(self.ids.button_menu)

	def close_button(self):
		self.add_widget(self.ids.button_dn)
		self.remove_widget(self.ids.button_menu)

class ManualControlScreen(Screen):
	def __init__(self, **kwargs):
		super(Screen,self).__init__(**kwargs)

		self.gear_val = 1

		self.D = Image(source='Img/d.png',
					allow_stretch= False,
					keep_ratio= True,
					pos_hint = {"center_x": 0.70, "center_y": 0.48},
						size_hint= (0.25, 0.25))

		self.R = Image(source='Img/r.png',
					allow_stretch= False,
					keep_ratio= True,
					pos_hint = {"center_x": 0.70, "center_y": 0.48},
						size_hint= (0.25, 0.25))

		self.left_arrow_image_normal = Image(
			source= 'Img/left_arrow.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.60, "center_y": 0.25},
			size_hint= (0.15, 0.15))

		self.right_arrow_image_normal = Image(
			source= 'Img/right_arrow.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.80, "center_y": 0.25},
			size_hint= (0.15, 0.15))

		self.left_arrow_image_down = Image(
			source= 'Img/left_arrow_dn.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.60, "center_y": 0.25},
			size_hint= (0.15, 0.15))

		self.right_arrow_image_down = Image(
			source= 'Img/right_arrow_dn.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.80, "center_y": 0.25},
			size_hint= (0.15, 0.15))

		self.add_widget(self.D)
		self.add_widget(self.right_arrow_image_normal)
		self.add_widget(self.left_arrow_image_normal)

	def run_all(self):
		accelerometer.enable()
		if GlobalShared.wifi == True:
			Clock.schedule_interval(self.send_all, 0.3)

	def disable_all(self):
		GlobalShared.direction = 0
		GlobalShared.speed = 0
		GlobalShared.forward_back = 1
		GlobalShared.left_arrow = 1
		GlobalShared.right_arrow = 1
		accelerometer.disable()
		Clock.schedule_once(self.disable_clock, 2)

	def disable_clock(self, dt):
		Clock.unschedule(self.send_all)
		Clock.unschedule(self.disable_clock)

	def send_all(self, dt):
		self.get_acceleration()
		direction_mess = str.encode('DI'+str(int(GlobalShared.direction))+'/')
		speed_mess = str.encode('SP'+str(int(GlobalShared.speed))+'/')
		forward_back_mess = str.encode('FB'+str(GlobalShared.forward_back)+'/')
		left_arrow_mess = str.encode('LA'+str(GlobalShared.left_arrow)+'/')
		right_arrow_mess = str.encode('RA'+str(GlobalShared.right_arrow))
		try:
			s.send(direction_mess+speed_mess+forward_back_mess+left_arrow_mess+right_arrow_mess)
		except IOError as exception:
			GlobalShared.error = True
			GlobalShared.wifi = False

	def get_acceleration(self):
		val = accelerometer.acceleration[:3]
		if val[1]:
			if val[1] > 5:
				GlobalShared.direction = 5
			elif val[1] < -5:
				GlobalShared.direction = -5
			else:
				GlobalShared.direction = val[1]
			GlobalShared.direction = -GlobalShared.direction

	def check_press(self):
		if self.gear_val == 1:
			if GlobalShared.speed < 20:
				if GlobalShared.wifi == True:
						GlobalShared.forward_back = 0

				self.replace_DonR()
				self.gear_val = 0
		elif self.gear_val == 0:
			if GlobalShared.speed < 20:
				if GlobalShared.wifi == True:
						GlobalShared.forward_back = 1

				self.replace_RonD()
				self.gear_val = 1

	def replace_DonR(self):
		self.remove_widget(self.D)
		self.add_widget(self.R)

	def replace_RonD(self):
		self.remove_widget(self.R)
		self.add_widget(self.D)

	def active_left_arrow(self, *args):
		GlobalShared.right_arrow = 1
		if args[1] == 'down':
			self.remove_widget(self.right_arrow_image_down)
			self.remove_widget(self.right_arrow_image_normal)
			self.remove_widget(self.left_arrow_image_normal)
			self.add_widget(self.right_arrow_image_normal)
			self.add_widget(self.left_arrow_image_down)
			GlobalShared.left_arrow = 0
		elif args[1] == 'normal':
			self.remove_widget(self.left_arrow_image_down)
			self.add_widget(self.left_arrow_image_normal)
			GlobalShared.left_arrow = 1

	def active_right_arrow(self, *args):
		GlobalShared.left_arrow = 1
		if args[1] == 'down':
			self.remove_widget(self.left_arrow_image_down)
			self.remove_widget(self.left_arrow_image_normal)
			self.remove_widget(self.right_arrow_image_normal)
			self.add_widget(self.left_arrow_image_normal)
			self.add_widget(self.right_arrow_image_down)
			GlobalShared.right_arrow = 0
		elif args[1] == 'normal':
			self.remove_widget(self.right_arrow_image_down)
			self.add_widget(self.right_arrow_image_normal)
			GlobalShared.right_arrow = 1

	def read_slider(self, *args):
		GlobalShared.speed = args[1]

class DatabaseScreen(Screen):
	def __init__(self, **kwargs):
		super(Screen,self).__init__(**kwargs)

		self.allowed_receive_database = True

		self.error = Image(
			source= 'Img/error.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.095, "center_y": 0.64},
			size_hint= (0.11, 0.11))

		self.wait = Image(
			source= 'Img/wait.png',
			allow_stretch= False,
			keep_ratio= True,
			pos_hint= {"center_x": 0.095, "center_y": 0.64},
			size_hint= (0.11, 0.11))

		graph_theme = {
			'label_options': {
				'color': rgb('444444'),  # color of tick labels and titles
				'bold': True},
			'background_color': rgb('f8f8f2'),  # back ground color of canvas
			'tick_color': rgb('808080'),  # ticks and grid
			'border_color': rgb('808080')}  # border drawn around each graph

		self.graph1 = Graph(
			xlabel='Time [s]',
			ylabel='Value',
			x_ticks_minor=5,
			x_ticks_major=5,
			y_ticks_minor = 1,
			y_ticks_major=10,
			y_grid_label=True,
			x_grid_label=True,
			padding=5,
			xlog=False,
			ylog=False,
			x_grid=False,
			y_grid=False,
			xmin=0,
			xmax=30,
			ymin=0,
			ymax=100,
			pos_hint={'center_x': 0.5, 'center_y':0.5},
			_with_stencilbuffer=False,
			**graph_theme)

		self.graph2 = Graph(
			xlabel='Time [s]',
			ylabel='Value',
			x_ticks_minor=5,
			x_ticks_major=5,
			y_ticks_minor = 1,
			y_ticks_major=1,
			y_grid_label=True,
			x_grid_label=True,
			padding=5,
			xlog=False,
			ylog=False,
			x_grid=False,
			y_grid=False,
			xmin=0,
			xmax=30,
			ymin=-5,
			ymax=5,
			pos_hint={'center_x': 0.5, 'center_y':0.5},
			_with_stencilbuffer=False,
			**graph_theme)

		self.plot1 = LinePlot(line_width=2, color=[1, 0, 0, 1])
		self.plot1.points = [(i, j*10/3) for i, j in enumerate(range(31))]
		self.graph1.add_plot(self.plot1)
		self.ids.panel1.add_widget(self.graph1)

		self.plot2 = LinePlot(line_width=2, color=[1, 0, 0, 1])
		self.plot2.points = [(i, j/3 -5) for i, j in enumerate(range(31))]
		self.graph2.add_plot(self.plot2)
		self.ids.panel2.add_widget(self.graph2)

	def wait_for_database(self, dt):
		self.allowed_receive_database = True
		self.remove_widget(self.error)
		self.remove_widget(self.wait)

	def get_database(self):
		if GlobalShared.wifi == True:
			if self.allowed_receive_database == True:
				self.allowed_receive_database = False
				Clock.schedule_once(self.wait_for_database, 2)
				check = None

				try:
					s.send(str.encode('DB'))
					answer = s.recv(4096)
					check = answer[-2:]
				except IOError as exception:
					GlobalShared.error = True
					GlobalShared.wifi = False

				if check == b'GD':
					self.data = pickle.loads(answer[:-2])
					if self.data != []:
						try:
							xmin = min([el[0] for el in self.data])
							xmax = max([el[0] for el in self.data])
							self.graph1.xmin = xmin
							self.graph1.xmax = xmax
							self.graph2.xmin = xmin
							self.graph2.xmax = xmax
							x_points = [el[0] for el in self.data]
							panel1_points = [el[1] for el in self.data]
							panel2_points = [el[2] for el in self.data]
							self.plot1.points = [el for el in zip(x_points, panel1_points)]
							self.plot2.points = [el for el in zip(x_points, panel2_points)]
							self.remove_widget(self.error)
							self.remove_widget(self.wait)
						except:
							pass
					else:
						self.remove_widget(self.error)
						self.remove_widget(self.wait)
						self.add_widget(self.error)
				elif check == b'':
					GlobalShared.error = True
					GlobalShared.wifi = False
					self.remove_widget(self.error)
					self.remove_widget(self.wait)
					self.add_widget(self.error)
				else:
					self.remove_widget(self.error)
					self.remove_widget(self.wait)
					self.add_widget(self.error)
			else:
				self.remove_widget(self.error)
				self.remove_widget(self.wait)
				self.add_widget(self.wait)
		else:
			self.remove_widget(self.error)
			self.remove_widget(self.wait)
			self.add_widget(self.error)

	def delete_all(self):
		self.remove_widget(self.wait)
		self.remove_widget(self.error)


class ChooseControlScreen(Screen):
	pass

class AutoControlScreen(Screen):
	
	def go(self):
		if GlobalShared.wifi == True:
			points_to_send = pickle.dumps(GlobalShared.points_array)
			try:
				s.send(str.encode('GO')+points_to_send)
			except IOError as exception:
				GlobalShared.error = True
				GlobalShared.wifi = False
			

class Painter(Widget):

	def __init__(self, **kwargs):
		super(Painter, self).__init__(**kwargs)

		self.allowed_draw = False

	def wait_for_draw(self, dt):
		self.allowed_draw = True

	def enter_drawing_window(self):
		self.allowed_draw = False
		Clock.schedule_once(self.wait_for_draw, 0.5)

	def on_touch_down(self, touch):
		with self.canvas:
			self.canvas.clear()
			self.count = 0
			GlobalShared.points_array = [[],[]]
			touch.ud["line"] = Line(points=(touch.x, touch.y))
			GlobalShared.points_array[0].append(int(touch.x))
			GlobalShared.points_array[1].append(int(touch.y))

	def on_touch_move(self, touch):
		if self.allowed_draw == True:
			touch.ud["line"].points += [touch.x, touch.y]
			if self.count % 3 == 0:
				GlobalShared.points_array[0].append(int(touch.x))
				GlobalShared.points_array[1].append(int(touch.y))	
			self.count += 1

class MyApp(App):
	global s
	s = None

	def on_start(self):
		self.android_set_hide_menu()

	def on_resume(self):
		self.android_set_hide_menu()

	def on_pause(self):
		return True

	def on_stop(self):
		Window.close()

	@run_on_ui_thread
	def android_set_hide_menu(self):
		if android_api_version.SDK_INT >= 19:
			Logger.debug('API >= 19. Set hide menu')
			view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
			view.setSystemUiVisibility(
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
				AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
				AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
				AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
				AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
				)

	def build(self):
		#Window.size = (1920, 1080)
		self.android_set_hide_menu()

		sm = ScreenManager(transition=SlideTransition())
		sm.add_widget(MenuScreen(name='menu'))
		sm.add_widget(ChooseControlScreen(name='choose_control'))
		sm.add_widget(ManualControlScreen(name='manual_control'))
		sm.add_widget(AutoControlScreen(name='auto_control'))
		sm.add_widget(DatabaseScreen(name='database'))

		return sm

if __name__ == '__main__':
	try:
		MyApp().run()
	except KeyboardInterrupt:
		if s: 
			s.close()