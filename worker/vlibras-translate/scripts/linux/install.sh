#!/bin/bash


read -r -p "Deseja fazer o download das dependências? [Y/n] " response
response=${response,,} # tolower
if [[ $response =~ ^(yes|y| ) ]]; then
 	cd ~
	git clone --single-branch --branch Python3 https://github.com/MoraesCaio/VLibras-python3.git open-signs
    # mkdir ~/open-signs
	cd open-signs

	# mkdir aelius
	# cd aelius

	# wget 150.165.204.30:8080/translate/linux/aelius-install.tar.gz

	# MACHINE_TYPE=`uname -m`
	# if [ ${MACHINE_TYPE} == 'x86_64' ]; then
	# 	wget 150.165.204.30:8080/translate/linux/hunpos/x86_64/hunpos-tag
	# else
	# 	wget 150.165.204.30:8080/translate/linux/hunpos/i386/hunpos-tag
	# fi

	chmod 777 vlibras-libs/aelius/bin/hunpos-tag

	read -r -p "Deseja instalar as dependências? [Y/n] " response
	response=${response,,} # tolower
	if [[ $response =~ ^(yes|y| ) ]]; then
	    # echo -e "\n# Extraindo...\n"
		# tar -xf aelius-install.tar.gz -C .
		# mkdir bin
		# mv hunpos-tag bin/

		echo -e "# Instalando dependências...\n"
		sudo apt-get update
		sudo apt-get install -y python-dev python-setuptools python-pip python-flask python-yaml python-numpy python-matplotlib
		pip3 install nltk flask-cors nltk_tgrep unidecode --upgrade

	fi

	# read -r -p "Deseja limpar os arquivos temporários? [Y/n] " response
	# response=${response,,} # tolower
	# if [[ $response =~ ^(yes|y| ) ]]; then
	# 	rm ~/vlibras-libs/aelius/aelius-install.tar.gz
	# fi

fi


read -r -p "Deseja criar as variáveis de ambiente? [Y/n] " response
response=${response,,} # tolower

if [[ $response =~ ^(yes|y| ) ]]; then

    # path to Hunpos Tag
	echo -e "\nHUNPOS_TAGGER=\"$HOME/open-signs/vlibras-libs/aelius/bin/hunpos-tag\"" >> ~/.bashrc
	echo -e "export HUNPOS_TAGGER" >> ~/.bashrc

	# path to Aelius Data
	echo -e "\nAELIUS_DATA=\"$HOME/open-signs/vlibras-libs/aelius/aelius_data\"" >> ~/.bashrc
	echo -e "export AELIUS_DATA" >> ~/.bashrc

	# path to Aelius Data
	echo -e "\nTRANSLATE_DATA=\"$HOME/open-signs/vlibras-translate/data\"" >> ~/.bashrc
	echo -e "export TRANSLATE_DATA" >> ~/.bashrc

	# path to NLTK Data
	echo -e "\nNLTK_DATA=\"$HOME/open-signs/vlibras-libs/aelius/nltk_data\"" >> ~/.bashrc
	echo -e "export NLTK_DATA" >> ~/.bashrc

	# path to Aelius and Translate package (new version)
	echo -e "\nPYTHONPATH=\"$HOME/open-signs/vlibras-libs/aelius:$HOME/open-signs/vlibras-translate/src:$HOME/open-signs/vlibras-translate/src/Ingles:$HOME/open-signs/vlibras-translate/src/Portugues:$HOME/open-signs/vlibras-translate/src/Espanhol:$HOME/open-signs/vlibras-translate/src/Templates:$HOME/open-signs/vlibras-translate/src/Templates:${PYTHONPATH}\"" >> ~/.bashrc
	echo -e "export PYTHONPATH\n" >> ~/.bashrc


	echo -e "\n## Execute o seguinte comando para concluir:\n\n$ source ~/.bashrc\n"
fi

echo -e "### Instalação finalizada!"
