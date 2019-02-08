for object in `ls $WINEPREFIX`;
    do ln -sf -T $WINEPREFIX/$object /var/local/shared_wine/wineprefix64/$object;
done
