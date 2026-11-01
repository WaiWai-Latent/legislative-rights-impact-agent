import pathlib
lines = pathlib.Path('src/reasoning.py').read_text().splitlines()
pathlib.Path('out.txt').write_text(repr(lines[28]))
print("wrote")