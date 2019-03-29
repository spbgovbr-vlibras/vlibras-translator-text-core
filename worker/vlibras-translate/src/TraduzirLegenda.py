import PortGlosa as pg

if __name__ == '__main__':

	name = input("Nome do arquvo: ")

	fl = open(name, 'r')

	lines = fl.readlines()
	fl.close()
	i = 0

	leg = []

	while i < len(lines):
		if lines[i].isspace():
			i += 1
			continue
		else:
			j = i+2
			text = []
			legIndex = int(lines[i].replace("\n",""))

			leg.append([legIndex,lines[i+1].replace("\n","")])

			while not lines[j].isspace():
				leg[legIndex-1].append(lines[j].replace("\n",""))
				j+=1

			i = j


	#print leg

	name = name[:-4] + "_glosa"

	out = open(name+".srt","w+")

	for i in range(len(leg)):
		for j in range(2,len(leg[i])):
			leg[i][j] = pg.traduzir(leg[i][j],"en")

	out.write("\n")

	for line in leg:
		out.write(str(line[0])+"\n")
		out.write(line[1]+"\n")

		for i in range(2,len(line)):
			out.write(line[i]+"\n")

		out.write("\n")

	out.close()
