files = ['general', 'ocr', 't2i', 'color']
for file in files:
    print(f'Testing {file}...')
    __import__(file)
