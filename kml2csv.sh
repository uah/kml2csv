#!/usr/bin/env bash

if [ -z "$1" ]; then
	echo "You didn't provide an input filename. URLs are also OK by me."
	exit 2
else
	ARG="$1"
	export ARG
fi

FILENAME="$(mktemp)"
if [ ! -f "$ARG" ]; then
	echo "That looks like a URL. Going to download it to $FILENAME"
	CMD="wget -qO- \"$ARG\" > \"$FILENAME\""
	echo "$CMD"
	echo "$CMD" | bash
else
    cp "$ARG" "$FILENAME"
fi

TEMPDIR="$(mktemp -d)"
if (file "$FILENAME" | grep "Zip archive data"); then
	echo "This is a zip file. Extracting."
	unzip -d "$TEMPDIR" "$FILENAME"
	FILENAME="$(find "$TEMPDIR" | grep -E '.kml$' | head -n 1)"
	if [ ! -z "$FILENAME" ]; then
		echo "The zip file had a kml file in it. Using this as our new file: $FILENAME"
	else
		echo "Nothing recognizable was in that zip file."
		exit 1
	fi
fi

NETWORKLINK="$(cat "$FILENAME" | grep NetworkLink -A 5 | xargs | sed -e 's/.*<href>//' -e 's/<\/href>.*//')"
if [ ! -z "$NETWORKLINK" ]; then
	echo "This is just a network link. Going to run: $0 \"$NETWORKLINK\""
	sleep 1 #failsafe sort of
	"$0" "$NETWORKLINK"; exit $?
fi

cd "$TEMPDIR"
mkdir out
CMD="/opt/kml2csv/venv3/bin/python /opt/kml2csv/KmlToCsv.py ${FILENAME} ${TEMPDIR}/out/"
echo "Running: $CMD"

if $CMD; then
    echo "Writing header file"

    HF="$TEMPDIR/out/00README.csv"
    echo "This dataset was generated on $(hostname -f)," > $HF
    echo "$(date) from the source map here:," >> $HF
    echo "$1" >> $HF
    echo "," >> $HF
    echo "Since this is an automatically-generated file it is inadvisable to edit it directly.," >> $HF
    echo "Please edit the source map instead.," >> $HF

	echo "Your output files are ready in this directory: ${TEMPDIR}/out"
fi



