
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

with open("Faxanadu (USA).nes", "rb") as file:
	ines_header = file.read(0x10)
	rom = bytearray(file.read())
	
with open("faxanadu_eo_font.chr", "rb") as file:
	font = file.read()
	patch(rom, font, 0x34000)
	
with open("text_eo.txt", "r", encoding = "utf-8") as file:
	raw_text = file.read();
	new_text = parse_text(raw_text)
	#print(new_text)
	patch(rom, new_text, 0x34300)
	
#Increase text speed
patch(rom, b"\x01", 0x3f49f)

#==========================================#==========================================#
#  TODO! Split text to not override stuff in the rom after the original script
#==========================================#==========================================#
	
with open("Faxanadu (EO).nes", "wb") as file:
	file.write(ines_header)
	file.write(rom)