import os
import subprocess
import sys


def translate(file_path):
    print('>>> TRANSLATING...')
    result = subprocess.run(['python', 'TraduzirArquivo.py', file_path])
    print('>>> TRANSLATION FINISHED.')
    return result


def translate_on_path(path, command):
    dirpath, _, filenames = next(os.walk(path))
    
    source_path = os.path.join(dirpath, 'source')
    glosa_path = os.path.join(dirpath, 'glosa')
    
    if not os.path.exists(source_path):
        os.makedirs(source_path)
    if not os.path.exists(glosa_path):
        os.makedirs(glosa_path)

    for filename in filenames:
        glosa_filename = filename[:-4]+'_glosa.txt'
        
        print(('>>> READING FILE:', os.path.join(dirpath, filename)))
        out = translate(os.path.join(dirpath, filename))
        
        print('>>> MOVING FILES:')
        os.rename(os.path.join(dirpath, filename),
                  os.path.join(source_path, filename))

        os.rename(os.path.join(dirpath, glosa_filename),
                  os.path.join(glosa_path, glosa_filename))
        print('>>> FINISHED.')


def main():
    for i in range(1, len(sys.argv)):
        translate_on_path(sys.argv[i], translate)


if __name__ == '__main__':
    main()
