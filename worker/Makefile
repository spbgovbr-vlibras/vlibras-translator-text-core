CURR_DIR	:=	$(shell pwd)
UTILS_PYCACHE	:=	"$(CURR_DIR)/core/utils/__pycache__"

CORE_CONFIG_FILE	:=	"$(CURR_DIR)/config/settings.ini"

install:
	@bash install.sh

start:
	@CORE_CONFIG_FILE=$(CORE_CONFIG_FILE) python3 core/worker.py

dev:
	@:$(eval CORE_CONFIG_FILE := "$(CURR_DIR)/config/settings-dev.ini")

clean:
	@echo -n "Cleaning... "
	@$(RM) -r $(UTILS_PYCACHE)
	@echo "\33[32;5mOK\033[m" || echo "\33[31;5mERROR\33[m"

.PHONY: install start dev clean