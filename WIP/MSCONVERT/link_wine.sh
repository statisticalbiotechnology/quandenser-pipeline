#!/bin/bash
for object in `ls $WINEPREFIX`;
    do ln -sf -T $WINEPREFIX/$object /tmp/wineprefix64_$USER/wineprefix64_$1/$object;
done
