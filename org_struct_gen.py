import re

FIELD_DELIMETER = '\t'
VALUES_DELIMETER = '|'
MAX_FIELD_VALUES = 10
PANEL_GROUP_TEMPLATE = './templates/template.group.html'
PANEL_TEMPLATE = './templates/template.group.panel.html'
BODY_TEMPLATE = './templates/template.group.panel.body.html'
FILE_INPUT = './files/input.txt'
FILE_OUTPUT = './files/output.txt'

class input_line(object):
	_text_raw = None
	_text = None
	level = None
	nextlevel = None
	values = []
	def __init__(self, pstring):
		self.level = re.search(r'[^' + FIELD_DELIMETER + ']', pstring).start()
		self._text_raw = pstring.strip()
		if (not self._text_raw): raise ValueError('No meaningful data found in the input string')
		val_num = self._text_raw.count(VALUES_DELIMETER)+1
		if MAX_FIELD_VALUES > val_num:
			self._text = self._text_raw + VALUES_DELIMETER * (MAX_FIELD_VALUES - val_num)
		values = self._text.split(VALUES_DELIMETER)
		self.values = [self._preprocess(v.strip(), i) for i, v in enumerate(values)]

	def _preprocess(self, val, indx):
		return val

class org_struct_gen(object):
	_body_template = None
	_panel_template = None
	_panel_group_template = None
	_input_lines = []
	def __init__(self):
		with open(BODY_TEMPLATE, 'r') as f:
			self._body_template=f.read()
		with open(PANEL_TEMPLATE, 'r') as f:
			self._panel_template=f.read()
		with open(PANEL_GROUP_TEMPLATE, 'r') as f:
			self._panel_group_template=f.read()
		with open(FILE_INPUT, 'r') as f:
			for l in f.readlines():
				self._input_lines.append(input_line(l))
		for i in range(0, len(self._input_lines)-1):
				self._input_lines[i].nextlevel = self._input_lines[i+1].level

	def _get_body(self, **kwargs):
		return self._body_template.format(**kwargs)

	def _get_panel(self, **kwargs):
		return self._panel_template.format(**kwargs)

	def _get_panel_group(self, group_id, *args):
		p = '\n'.join(args)
		return self._panel_group_template.format(group_id=group_id, panels=p)
	_current_level = 0
	_current_index = 0

	def create(self, parent_id=''):
		lid = 0
		panels = []
		while self._current_index < len(self._input_lines): 
			l = self._input_lines[self._current_index] 
			if l.level == self._current_level: # panel must be printed on this level
				panel_id = '{:02d}'.format(lid)
				if parent_id: panel_id = '{0}_{1}'.format(parent_id, panel_id)
				lid += 1
				self._current_index += 1
				#print('\t'*self._current_level, panel_id, l.values[0])
				if l.nextlevel is None:  # last input line, exiting
					parms = { 
						'name': l.values[1], 
						'description': l.values[2] 
					}
					panels.append( self._get_panel(parent_id=parent_id, panel_id=panel_id, header=l.values[0], body=self._get_body(**parms)))
					return self._get_panel_group(parent_id, *panels)
				if l.nextlevel > l.level: # nested panels, recursion
					self._current_level += 1
					parms = { 
						'name': l.values[1], 
						'description': l.values[2] 
					}
					body = self._get_body(**parms) + self.create(panel_id) # nested panels must be the part of panel body
					panels.append( self._get_panel(parent_id=parent_id, panel_id=panel_id, header=l.values[0], body=body))
					self._current_level -= 1
				else: # just ordinary panel on current level
					parms = { 
						'name': l.values[1], 
						'description': l.values[2] 
					}
					panels.append( self._get_panel(parent_id=parent_id, panel_id=panel_id, header=l.values[0], body=self._get_body(**parms)))
			if l.level < self._current_level: # panel should not be printed on this level, leaving one more nested level
				return self._get_panel_group(parent_id, *panels)
			if l.nextlevel < l.level: # current level ending, return from recursion
				return self._get_panel_group(parent_id, *panels)
		return self._get_panel_group(parent_id, *panels)

# entry point:
with open(FILE_OUTPUT, 'w') as f: f.write(org_struct_gen().create())
