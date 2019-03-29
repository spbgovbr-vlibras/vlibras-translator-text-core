#!/bin/bash

if [ "$1" == "clean" ]; then
	/etc/init.d/translation-server stop
	sudo update-rc.d -f translation-server remove

	if [ -f /etc/init.d/translation-server ]; then
		sudo rm /etc/init.d/translation-server
	fi
	
else
	read -r -p "Em qual porta o serviço rodará? " response
	port=${response,,} # tolower

	read -r -p "Qual modo [translate|dict|full] deseja executar o serviço? " response
	mode=${response,,} # tolower

	sudo cp translation-server /etc/init.d/
	cd /etc/init.d

	sudo sed -i 's/####PORT####/'$port'/g' translation-server
	sudo sed -i 's/####MODE####/'$mode'/g' translation-server
	sudo sed -i 's/####USER####/'$USER'/g' translation-server

	hunpos_tagger=`echo $HUNPOS_TAGGER`
	aelius_data=`echo $AELIUS_DATA`
	nltk_data=`echo $NLTK_DATA`
	translate_data=`echo $TRANSLATE_DATA`
	pythonpath=`echo $PYTHONPATH`
	
	sudo sed -i 's|####HUNPOS####|'$hunpos_tagger'|g' translation-server
	sudo sed -i 's|####AELIUS####|'$aelius_data'|g' translation-server
	sudo sed -i 's|####NLTK####|'$nltk_data'|g' translation-server
	sudo sed -i 's|####TRANSLATE####|'$translate_data'|g' translation-server
	sudo sed -i 's|####PYTHON####|'$pythonpath'|g' translation-server

	if [ $mode != "translate" ]; then
		signs_vlibras=`echo $SIGNS_VLIBRAS`
    	sudo sed -i 's|####SIGNS####|'$signs_vlibras'|g' translation-server
	fi

	sudo chmod 755 translation-server
	/etc/init.d/translation-server stop
	sudo update-rc.d -f translation-server remove
	sudo update-rc.d translation-server defaults
	/etc/init.d/translation-server start
fi