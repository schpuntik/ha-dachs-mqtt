from .zumdachs import ZumDachs

# Создаём словарь: ключ → запись
ZUM = {entry[1]: entry for entry in ZumDachs}

SECTORS = {

    # ---------------------------------------------------------
    # BASIC (основные данные)
    # ---------------------------------------------------------
    "basic": [
        ZUM["Hka_Bd.Anforderung.ModulAnzahl"],
        ZUM["Hka_Bd.Anforderung.UStromF_Anf.bFlagSF"],
        ZUM["Hka_Bd.UStromF_Frei.bFreigabe"],
        ZUM["Hka_Bd.bStoerung"],
        ZUM["Hka_Bd.bWarnung"],
        ZUM["Hka_Bd.UHka_Anf.Anforderung.fStrom"],
        ZUM["Hka_Bd.UHka_Anf.usAnforderung"],
        ZUM["Hka_Bd.UHka_Frei.usFreigabe"],
        ZUM["Hka_Bd.ulArbeitElektr"],
        ZUM["Hka_Bd.ulArbeitThermHka"],
        ZUM["Hka_Bd.ulArbeitThermKon"],
        ZUM["Hka_Bd.ulBetriebssekunden"],
        ZUM["Hka_Bd.ulAnzahlStarts"],
        ZUM["Hka_Bd_Stat.uchSeriennummer"],
        ZUM["Hka_Bd_Stat.uchTeilenummer"],
        ZUM["Hka_Bd_Stat.ulInbetriebnahmedatum"],
    ],

    # ---------------------------------------------------------
    # BD3112 – годовые данные
    # ---------------------------------------------------------
    "bd3112": [
        ZUM["BD3112.Hka_Bd.ulBetriebssekunden"],
        ZUM["BD3112.Hka_Bd.ulAnzahlStarts"],
        ZUM["BD3112.Hka_Bd.ulArbeitElektr"],
        ZUM["BD3112.Hka_Bd.ulArbeitThermHka"],
        ZUM["BD3112.Hka_Bd.ulArbeitThermKon"],
        ZUM["BD3112.Ww_Bd.ulWwMengepA"],
    ],

    # ---------------------------------------------------------
    # BRENNER – второй теплогенератор
    # ---------------------------------------------------------
    "brenner": [
        ZUM["Brenner_Bd.bIstStatus"],
        ZUM["Brenner_Bd.bWarnung"],
        ZUM["Brenner_Bd.UBrenner_Anf.usAnforderung"],
        ZUM["Brenner_Bd.UBrenner_Frei.bFreigabe"],
        ZUM["Brenner_Bd.ulAnzahlStarts"],
        ZUM["Brenner_Bd.ulBetriebssekunden"],
    ],

    # ---------------------------------------------------------
    # HYDRAULIK
    # ---------------------------------------------------------
    "hydraulik": [
        ZUM["Hka_Ew.HydraulikNr.bSpeicherArt"],
        ZUM["Hka_Ew.HydraulikNr.bWW_Art"],
        ZUM["Hka_Ew.HydraulikNr.b2_Waermeerzeuger"],
        ZUM["Hka_Ew.HydraulikNr.bMehrmodul"],
    ],

    # ---------------------------------------------------------
    # TEMPERATUREN
    # ---------------------------------------------------------
    "temperaturen": [
        ZUM["Hka_Mw1.Temp.sAbgasHKA"],
        ZUM["Hka_Mw1.Temp.sAbgasMotor"],
        ZUM["Hka_Mw1.Temp.sKapsel"],
        ZUM["Hka_Mw1.Temp.sbAussen"],
        ZUM["Hka_Mw1.Temp.sbFreigabeModul"],
        ZUM["Hka_Mw1.Temp.sbFuehler1"],
        ZUM["Hka_Mw1.Temp.sbFuehler2"],
        ZUM["Hka_Mw1.Temp.sbGen"],
        ZUM["Hka_Mw1.Temp.sbMotor"],
        ZUM["Hka_Mw1.Temp.sbRegler"],
        ZUM["Hka_Mw1.Temp.sbRuecklauf"],
        ZUM["Hka_Mw1.Temp.sbVorlauf"],
        ZUM["Hka_Mw1.Temp.sbZS_Fuehler3"],
        ZUM["Hka_Mw1.Temp.sbZS_Fuehler4"],
        ZUM["Hka_Mw1.Temp.sbZS_Vorlauf1"],
        ZUM["Hka_Mw1.Temp.sbZS_Vorlauf2"],
        ZUM["Hka_Mw1.Temp.sbZS_Warmwasser"],
        ZUM["Hka_Mw1.Solltemp.sbRuecklauf"],
        ZUM["Hka_Mw1.Solltemp.sbVorlauf"],
    ],

    # ---------------------------------------------------------
    # AKTOREN
    # ---------------------------------------------------------
    "aktoren": [
        ZUM["Hka_Mw1.Aktor.bWwPumpe"],
        ZUM["Hka_Mw1.Aktor.fFreiAltWaerm"],
        ZUM["Hka_Mw1.Aktor.fMischer1Auf"],
        ZUM["Hka_Mw1.Aktor.fMischer1Zu"],
        ZUM["Hka_Mw1.Aktor.fMischer2Auf"],
        ZUM["Hka_Mw1.Aktor.fMischer2Zu"],
        ZUM["Hka_Mw1.Aktor.fProgAus1"],
        ZUM["Hka_Mw1.Aktor.fProgAus2"],
        ZUM["Hka_Mw1.Aktor.fProgAus3"],
        ZUM["Hka_Mw1.Aktor.fStoerung"],
        ZUM["Hka_Mw1.Aktor.fUPHeizkreis1"],
        ZUM["Hka_Mw1.Aktor.fUPHeizkreis2"],
        ZUM["Hka_Mw1.Aktor.fUPKuehlung"],
        ZUM["Hka_Mw1.Aktor.fUPVordruck"],
        ZUM["Hka_Mw1.Aktor.fUPZirkulation"],
        ZUM["Hka_Mw1.Aktor.fWartung"],
        ZUM["Hka_Mw1.sWirkleistung"],
        ZUM["Hka_Mw1.ulMotorlaufsekunden"],
        ZUM["Hka_Mw1.usDrehzahl"],
    ],

    # ---------------------------------------------------------
    # TAGESLAUF – 15‑минутные интервалы
    # ---------------------------------------------------------
    "tageslauf": [
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[0]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[1]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[2]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[3]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[4]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[5]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[6]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[7]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[8]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[9]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[10]"],
        ZUM["Laufraster15Min_aktTag.bDoppelstunde[11]"],
    ],

    # ---------------------------------------------------------
    # MEHRMODULTECHNIK
    # ---------------------------------------------------------
    "mehrmodul": [
        ZUM["Mm[0].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[0].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[1].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[1].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[2].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[2].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[3].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[3].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[4].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[4].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[5].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[5].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[6].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[6].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[7].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[7].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[8].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[8].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm[9].ModulSteuerung.fModulLaeuft"],
        ZUM["Mm[9].ModulSteuerung.fModulVerfuegbar"],
        ZUM["Mm_MinMax.bModulBhMaxWart"],
        ZUM["Mm_MinMax.bModulBhMinWart"],
        ZUM["Mm_MinMax.sBhMaxWart"],
        ZUM["Mm_MinMax.sBhMinWart"],
        ZUM["Mm_MinMax.ModulBhMax.bModulNr"],
        ZUM["Mm_MinMax.ModulBhMax.ulWert"],
        ZUM["Mm_MinMax.ModulBhMin.bModulNr"],
        ZUM["Mm_MinMax.ModulBhMin.ulWert"],
        ZUM["Mm_MinMax.ModulStartMax.bModulNr"],
        ZUM["Mm_MinMax.ModulStartMax.ulWert"],
        ZUM["Mm_MinMax.ModulStartMin.bModulNr"],
        ZUM["Mm_MinMax.ModulStartMin.ulWert"],
    ],

    # ---------------------------------------------------------
    # WARTUNG
    # ---------------------------------------------------------
    "wartung": [
        ZUM["Wartung_Cache.fStehtAn"],
        ZUM["Wartung_Cache.ulBetriebssekundenBei"],
        ZUM["Wartung_Cache.ulZeitstempel"],
        ZUM["Wartung_Cache.usIntervall"],
    ],
}
