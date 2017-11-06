#coding: utf-8
import appex, requests, ui, re, clipboard, photos, Image, console
from io import BytesIO
from objc_util import ObjCInstance

@ui.in_background
def origin_text ():
	if appex.is_running_extension():
		view.origin_text.text = appex.get_text() or requests.get(appex.get_url()).text
	elif clipboard.get().startswith('http') and not clipboard.get().endswith('.js'):
		if requests.head(clipboard.get()).headers.get('Content-Type','/').split('/')[0] == 'text':
			view.origin_text.text = '正在载入...'
			view.origin_text.text = requests.get(clipboard.get(),timeout=10).text
		else:
			view.origin_text.text = clipboard.get()
	elif clipboard.get().startswith('http') and clipboard.get().endswith('.js'):
		view.origin_text.text = '正在载入...'
		view.origin_text.text = requests.get(clipboard.get(),timeout=10).text
	else:
		view.origin_text.text = clipboard.get()

def match_text ():
	try:
		match = re.findall(view.expression_input.text,view.origin_text.text,re.I)
		view.match_count.title = str(len(match))
		return match
	except:
		return []

class ExpressionInputDelegate (object):
	
	def textfield_did_end_editing(self,textfield):
		global match_res
		if textfield.text:
			match_res = match_text()
			view.match_text.reload_data()
	
	def textfield_did_change (self,textfield):
		view.match_button.enabled = True if textfield.text else False

class MatchDataSource (object):
	def tableview_number_of_rows(self, tableview, section):
		return len(match_res)
	
	def tableview_can_delete(self,tableview,section,row):
		return False
	
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		cell.bg_color = 'white'
		cell.text_label.number_of_lines = 0
		cell.text_label.text = match_res[row]
		cell.text_label.font = ('<System>',16)
		return cell

class MatchDelegate (object):
	def tableview_did_select(self, tableview, section, row):
		self.select = match_res[row]
		preview = ui.WebView()
		preview.load_url(requests.utils.unquote(self.select).replace('\\',''))
		preview.name = '预览'
		copy_button = ui.ButtonItem()
		copy_button.title = '复制URL'
		copy_button.action = self.copy_button_tapped
		preview.right_button_items = [copy_button]
		save_button = ui.ButtonItem()
		save_button.title = '     保存'
		save_button.action = self.save_button_tapped
		preview.left_button_items = [save_button]
		if match_res[row].startswith('http'):
			preview.present()
	
	def copy_button_tapped (self,sender):
		clipboard.set(self.select)
	
	@ui.in_background	
	def save_button_tapped (self,sender):
		try:
			photos.save_image(Image.open(BytesIO(requests.get(self.select).content)))
		except:
			pass
			

class RootView (ui.View):
	
	def __init__ (self):
		self.bg_color = '#ecf5f5'
		self.name = '正则表达式测试'
		self.copy_button = ui.ButtonItem()
		self.copy_button.title = '复制表达式'
		self.copy_button.action = self.copy_button_tapped
		self.right_button_items = [self.copy_button]
		self.match_count = ui.ButtonItem()
		self.match_count.title = '0'
		self.match_count.tint_color = 'red'
		self.left_button_items = [self.match_count]
		
		self.expression_input = ui.TextField()
		self.expression_input.frame = (10,6,w-70,40)
		self.expression_input.border_width = 1
		self.expression_input.corner_radius = 6
		self.expression_input.clear_button_mode = 'always'
		self.expression_input.placeholder = '输入表达式'
		self.expression_input.delegate = ExpressionInputDelegate()
		self.expression_input.text = "http[^,;\"!<>]+?\.jpg"
		
		self.match_button = ui.Button()
		self.match_button.image = ui.Image.named('iow:ios7_circle_filled_256')
		self.match_button.frame = (w-50,6,37,40)
		self.match_button.action = self.match_button_tapped
		self.match_button.tint_color = 'green'
		#self.match_button.enabled = False
		
		self.origin_text = ui.TextView()
		self.origin_text.frame = (10,self.expression_input.y+self.expression_input.height+10,w-20,350)
		self.origin_text.bg_color = 'white'
		self.origin_text.border_width = 1
		self.origin_text.corner_radius = 6
		self.origin_text.number_of_lines = 0
		self.origin_text.font = ('<System>',16)

		self.match_text = ui.TableView()
		self.match_text.size_to_fit()
		self.match_text.bg_color = 'white'
		self.match_text.border_width = 1
		self.match_text.corner_radius =  6
		ObjCInstance(self.match_text).estimatedRowHeight = 1
		self.match_text.data_source = MatchDataSource()
		self.match_text.delegate = MatchDelegate()
		self.add_subview(self.expression_input)
		self.add_subview(self.match_button)
		self.add_subview(self.origin_text)
		self.add_subview(self.match_text)

		
	def draw (self):
		self.match_text.frame = (10,self.origin_text.y+self.origin_text.height+10,w-20,h-self.origin_text.y-self.origin_text.height-85)
		
	def touch_moved (self,touch):
		y = touch.location[-1]
		if h-170 > y > 140:
			self.origin_text.height = y-self.origin_text.y
			self.set_needs_display()
	
	def match_button_tapped (self,sender):
		global match_res
		match_res = match_text()
		self.match_text.reload_data()
		
	def copy_button_tapped (self,sender):
		clipboard.set(self.expression_input.text)

if __name__ == '__main__':
	origin_text()
	match_res = []
	w,h = ui.get_screen_size()
	view = RootView()
	view.present()
