import sys
import PortGlosa as pg

if __name__ == '__main__':

    with open(sys.argv[1], 'r') as input_file:
        with open(sys.argv[1][:-4]+'_glosa.txt', 'w') as output_file:
            for index, line in enumerate(input_file):
                output_file.write(pg.traduzir(line.replace("\n", "").replace(',', '')) + "\n")
                print(index)
