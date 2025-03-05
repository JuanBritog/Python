def get_italian_month(mese):
    mesi_italiani = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    return mesi_italiani[mese - 1] if 1 <= mese <= 12 else "Mese non valido"
