DIR_NAME = "${shell: date --iso}"

current:
	mkdir -p "${DIR_NAME}"
	rm -rf .current
	ln -s "${DIR_NAME}" .current

