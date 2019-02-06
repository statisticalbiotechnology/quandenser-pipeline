for object in `ls $WINEPREFIX`;
    do ln -s -T $WINEPREFIX/$object /home/$USER/wineprefix64/$object;
done
