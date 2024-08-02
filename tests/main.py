files = ['general', 'ocr', 't2i']
for file in files:
    print(f'Testing {file}...')
    __import__(file)
