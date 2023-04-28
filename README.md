## Implementačná dokumentácia k 2. úlohe do IPP 2021/2022
#### Meno a priezvisko: Veronika Molnárová
#### Login: xmolna08

---

### Popis projektu
Cieľom projektu bolo vytvoriť dva skripty, prvý v jazyku python ako interpret jazyka IPPcode22, ktorý by mal prakticky naväzovat na parser z prvej časti projektu a druhý skript v jazyku PHP na otestnovanie funkcionality implementovaného parseru aj interpretu. V prípade volania skriptov s argumentom *--help* je vypísaná nápoveda a program následne ukončený.

### Interpret jayzka IPPcode22
Skript je možné volať s dvoma argumentmi, *--source* a *--intup*, ktoré predstavujú vstupný súbor so zdrojovým kódom(XML reprezentácia inštrukcií) a súbor so vstupom v pre prípadnú inštrukciu READ. V prípade vynechania jedného argumentu je daný vstup braný zo štandardného vstupu, neuvedenie ani jedného argumentu ale vedie na chybu. Výstupom je buď výstup po vykonaní programu v jazyku IPPcode22 alebo nájdená sémantická či behová chyba.

Program prvotne prejde vstupnú XML štruktúru pomocou python knižnice *xml.etree.ElementTree*, ktorú skontroluje na chyby nesprávnej syntaxe. Následne je vytvorená vnútorná reprezentácia programu uložená vo vytvorených triedach *Program*, *Instruction*, *Argument*. Jednotlivé druhy inštrukcií sú tvorené pomocou triednej metódy triedy *MakeInstruct*, ktorá funguje ako továreň inštrukcií. Pre každú inštrukciu je odvodená samostatná podtrieda z triedy *Instruction*, ktorá má implementovanú svoju danú funkciounalitu.
Pre účely pamäťového modelu programu boli implementované pamäťové rámce a zásobník rámcov v triedach *GlobalFrame* s podtriedou *SingleFrame*(reprezentuje lokálny aj dočasný rámec) a trieda *FrameStack*. Pre zásobníkové inštrukcie bol vytvorený dátový zásobník *data_stack* ako list z jazyka python.
Posledne *LabelDict* je trieda slúžiaca ako slovník náveští spoločne so zásobníkom volaní a čítačom inštrukcií.

Po vytvorení stromovej štruktúry programu sú dané inštrukcie zoradené, skontrolované na správne očíslovanie a jednotlivé náveštia sú načítané do slovníka. Beh programu sa riadi podľa čítača inštrukcií, ktorý v cykle volá jednotlivé vykonania inštrukcií, pokým sa nepríde na koniec programu alebo je beh násilne pozastavený inštrukciou *EXIT*.


### Skript na testovanie
Skript neberie žiadny vstup, všetky potrebné informáciu sú mu predané pomocou argumentov programu, ktoré špecifikujú jednotlivé skripty na testovanie(--int-script, --parse-script), štýl, akým sa majú testovať(--int-only, --parse-only, --recursive, --noclean), adresár s jednotlivými testmi(--directory) a jexaxml súbor(--jexampath), pomocou ktorého sa porovnávajú XML súbory. Výstupom testovania je HTML stránka vypísaná na štandardný výstup, ktorá obsahuje jednotlivé výsledky testovania. V prípade nastania chyby počas testov je testovanie ukončené vypísaním chybovej hlášky.

Jednotlivé argumenty sú načítané do instancie triedy *Arguments*, ktorá implementuje funkcie na skontrolovanie existenie jednotlivých súborov a správnej kombinácie argumentov. Následne sú prechádzané jednotlivé súbory v testovacom priečinku hladajúc súbory s príponov *.src* obsahujúce zdrojový kód pre testovaný skript. V prípade nastavenia argumentu *--recursive* sú rekurzívne prehľadávané všetky zanorené priečinky. Testovaciu sadu okrem súboru *.src* dopĺňajú súbory *.in*, *.out*, *.rc*, ktoré sú prípadne dogenerované so základnými hodnotami. Podľa nastavenia testov sa otestuje určený skript na správny návratový kód a prípade úspešného behu aj správny výstup ku referenčnému. V prípade behu testov na oboch skriptoch zároveň je výstup z parseru uložený do dočasného súboru predstavujúci vstup pre interpret, ak neprišlo ku chybu. V prípade nastavenia argumentu *--noclean* sú tieto dočastné súbory ponechané.


