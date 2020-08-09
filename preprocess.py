import sys

def unescape_x_system(text):
    return text.replace("cx", "ĉ")\
        .replace("gx", "ĝ")\
        .replace("hx", "ĥ")\
        .replace("jx", "ĵ")\
        .replace("sx", "ŝ")\
        .replace("ux", "ŭ")
        
with open(sys.argv[1], "r", encoding="utf-8") as file:
    text = file.read()
    
with open(sys.argv[1], "w", encoding="utf-8") as file:
    file.write(unescape_x_system(text))