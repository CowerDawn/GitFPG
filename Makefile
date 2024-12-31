PROGRAM_NAME = gitfpg
INSTALL_PATH = /usr/bin
ICON_PATH = fpg.png
DESKTOP_FILE_PATH = /usr/share/applications/$(PROGRAM_NAME).desktop
PYINSTALLER_CMD = pyinstaller --onefile --windowed --icon=$(ICON_PATH) $(PROGRAM_NAME).py

all: build install

build:
	$(PYINSTALLER_CMD)

install:
	sudo cp dist/$(PROGRAM_NAME) $(INSTALL_PATH)/$(PROGRAM_NAME)
	sudo chmod +x $(INSTALL_PATH)/$(PROGRAM_NAME)
	convert -size 256x256 xc:white -font Arial -pointsize 50 -fill black -draw "text 50,150 'FPG'" $(ICON_PATH)
	echo "[Desktop Entry]\nType=Application\nName=$(PROGRAM_NAME)\nExec=$(INSTALL_PATH)/$(PROGRAM_NAME)\nIcon=$(PWD)/$(ICON_PATH)\nCategories=Utility;" | sudo tee $(DESKTOP_FILE_PATH) > /dev/null

clean:
	rm -rf build dist $(PROGRAM_NAME).spec
	sudo rm -f $(INSTALL_PATH)/$(PROGRAM_NAME) $(DESKTOP_FILE_PATH)
