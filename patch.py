
def patch(rom, new_data, pos):
	for i, val in enumerate(new_data):
		rom[pos + i] = val

special_chars = {
	'ĉ': 0x3a,
	'ĝ': 0x3b,
	'ĥ': 0x3c,
	'ĵ': 0x3d,
	'ŝ': 0x3e,
	'ŭ': 0x5b,
	'Ĉ': 0x3a,
	'Ĝ': 0x3b,
	'Ĥ': 0x3c,
	'Ĵ': 0x3d,
	'Ŝ': 0x3e,
	'Ŭ': 0x5b,
	' ': 0xfd,
	'/': 0xfc,	# A-press
	'~': 0xfb,	# Title
	'\n': 0xfe
}

def parse_char(c):
	if c in special_chars:
		return special_chars[c]
	else:
		return ord(c)
	
def remove_single_comment(line):
	if '#' in line:
		return line[:line.index('#')]
	else:
		return line

def is_good_dialog(dialog, index):
	a_press_indices = [index for index, line in enumerate(dialog) if '/' in line]
	is_good_a_press = map(lambda end, start: end - start <= 4, a_press_indices[1:], a_press_indices)
	assert all(is_good_a_press), "Dialog " + hex(index + 1) + ": Not enough A-presses."
	
	is_good_line = map(
		lambda line: len(line) <= 16 or len(line) == 17 and line[-1] == '/',
		dialog
	)
	assert all(is_good_line), "Dialog " + hex(index + 1) + ": Line too long."

def parse_word(word):
	return bytes(map(parse_char, word))
	
def parse_single_line(line):
	words = map(parse_word, line.split(' '))
	return b"\xfd".join(words)

def parse_dialog(dialog):
	new_dialog = []
	for i, line in enumerate(map(parse_single_line, dialog)):
		if i != len(dialog) - 1 and len(line) < 16:
			new_dialog.append(line + b"\xfe")
		else:
			new_dialog.append(line)
	return b"".join(new_dialog)

def parse_text(text):
	lines = text.splitlines()
	lines = map(remove_single_comment, lines)				#Remove comments
	lines = list(filter(lambda l: len(l.strip()) != 0, lines))	#Remove blank lines
	
	#Separate dialogs
	dialog_sep_indices = [-1] + [index for index, line in enumerate(lines) if line.strip() == "==="]
	dialogs = list(map(lambda start, end: lines[start + 1:end], dialog_sep_indices, dialog_sep_indices[1:]))
	for i, d in enumerate(dialogs):
		is_good_dialog(d, i)
		
	return b"\xff".join(map(parse_dialog, dialogs))

#===========================================

item_names = [
	"PONARDO",			#hand dagger
	"LONGA GLAVO",		#long sword
	"TRIOBLA KLINGO",	#giant blade
	"DRAKMORTIGANTO",	#dragon slayer
	"LEDA ARMAĴO",		#leather armor
	"GARNITA VESTO",	#studded mail
	"PLENA KIRASO",		#full plate
	"BATALA ARMAĴO",	#battle suit
	"ETA ŜILDO",		#small shield
	"GRANDA ŜILDO",		#large shield
	"MAGIA ŜILDO",		#magic shield
	"BATALA KASKO",		#battle helmet
	"DILUVO",			#deluge
	"TONDRO",			#thunder
	"FAJRO",			#fire
	"MORTO",			#death
	"TILT",				#tilt
	"RINGO DE ELFOJ",	#ring of elf
	"RUBENA RINGO",		#ruby ring
	"RINGO DE NANOJ",	#ring of dworf
	"DEMONA RINGO",		#demon's ring
	"ŜLOSILO A",		#key a
	"ŜLOSILO K",		#key k
	"ŜLOSILO Q",		#key q
	"ŜLOSILO J",		#key j
	"ŜLOSILO JO",		#key jo
	"PIKPIOĈO",			#mattock
	"MAGIA VERGO",		#rod		(unused)
	"KRISTALO",			#crystal	(unused)
	"LAMPO",			#lamp		(unused)
	"SABLOHORLOĜO",		#hour glass
	"LIBRO",			#book		(unused)
	"FLUGANTAJBOTOJ",	#wing boots
	"RUĜA TRINKAĴO",	#red potion
	"NIGRA TRINKAĴO",	#black potion (unused)
	"ELIKSIRO",			#elixir		(unused)
	"KOLIERO",			#pendant	(unused)
	"NIGRA ONIKSO",		#black onix	(unused)
	"FAJRA KRISTALO"	#fire crystal (unused)
]

special_chars_items = {
	'Ĉ': b'C',
	'Ĝ': b'G',
	'Ĥ': b'H',
	'Ĵ': b'J',
	'Ŝ': b'S',
	'Ŭ': b'U'
}

hat_chars = ['Ĉ', 'Ĝ', 'Ĥ', 'Ĵ', 'Ŝ']

breve_chars = ['Ŭ']

def flatten_list_of_bytes(list):
	return bytes([int(byte) for byte_list in list for byte in byte_list])

def remove_accents(text):
	return flatten_list_of_bytes([special_chars_items[a] if a in special_chars_items else bytes([ord(a)]) for a in text])

def get_accent(char):
	if char in hat_chars:
		return b'\x01'
	elif char in breve_chars:
		return b'\x02'
	else:
		return b'\x00'

def isolate_accents(text):
	return flatten_list_of_bytes([get_accent(a) for a in text])

def parse_item_names(names):
	text = [remove_accents(name) for name in names]
	accents = [isolate_accents(name) for name in names]
	return text, accents
	
def create_memory_from_text(text):
	length = len(text)
	return bytes([length]) + text + bytes(15 - length)
	
def create_memory_from_item_names(names):
	text, accents = parse_item_names(names)
	text_mem = flatten_list_of_bytes([create_memory_from_text(t) for t in text])
	accents_mem = flatten_list_of_bytes([create_memory_from_text(a) for a in accents])
	return text_mem, accents_mem

with open("Faxanadu (USA).nes", "rb") as file:
	ines_header = file.read(0x10)
	rom = bytearray(file.read())
	
with open("faxanadu_eo_font.chr", "rb") as file:
	font = file.read()
	patch(rom, font, 0x34000)
	
with open("faxanadu_eo_font_menus.chr", "rb") as file:
	font = file.read()
	patch(rom, font, 0x28200)
	
with open("text_eo.txt", "r", encoding = "utf-8") as file:
	raw_text = file.read();
	new_text = parse_text(raw_text)
	patch(rom, new_text, 0x34300)
	
text_mem, accents_mem = create_memory_from_item_names(item_names)
patch(rom, text_mem, 0x31b3d)
patch(rom, accents_mem, 0x32d90)
	
#Increase text speed
patch(rom, b"\x01", 0x3f49f)
	
with open("Faxanadu (EO).nes", "wb") as file:
	file.write(ines_header)
	file.write(rom)