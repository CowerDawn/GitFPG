TARGET = gitfpg

all: install

install:
	pyinstaller --onefile $(TARGET).py
	sudo cp dist/$(TARGET) /usr/bin/$(TARGET)
	sudo chmod +x /usr/bin/$(TARGET)

uninstall:
	sudo rm -f /usr/bin/$(TARGET)

run:
	python $(TARGET).py

clean:
	rm -rf __pycache__ build dist $(TARGET).spec
