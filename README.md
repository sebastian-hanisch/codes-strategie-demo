# Codes als Strategie: Hüte, Summen und das Schachbrett – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-codes-strategie-demo.streamlit.app/)**

Zweites Stück der Reihe **Teamrätsel** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Ein Team hat **ein gemeinsames Ziel**, darf **vorher eine Strategie absprechen**, und handelt dann mit **beschränkter Information** (keine Verständigung währenddessen). Diese Demo zeigt **vier bekannte Rätsel mit demselben Trick**: eine **Prüfsumme** (eine Summe modulo q, bei zwei Farben das XOR) ordnet jedem Mitglied einen Wert zu, den es aus dem Gesehenen ausrechnen kann. Die Kulissen: **Hüte gleichzeitig** (raten oder passen; bei drei Spielern die Strategie für drei Hüte, der Hamming-Code der Länge 3, bei sieben Spielern der Hamming-Code der Länge 7), **Hüte in einer Reihe** (die Summe wird angesagt), **Summen-Hüte** (genau ein Tipp richtig) und das **Schachbrett** (ein umgedrehtes Feld überträgt sechs Bit). Es gibt keine Kulisse aus der Logistik; es sind Lehrbuch-Rätsel mit festen Annahmen.

**Die Rätsel sind bekanntes Lehrbuchwissen**; eigen ist der Vergleich der vier Kulissen und dass jede Zahl der Demo ausgezählt oder bewiesen ist, ausgenommen die ausdrücklich genannten Stichproben (64-Felder-Brett, lange Reihen) und der Wert der besten Strategie bei n = 8 (Löserergebnis, Optimalität in der Testsuite nicht nachgerechnet, siehe Grenzen). Die Aufzählung aller Strategien bei drei Hüten, das ganzzahlige Modell für die beste Strategie und die Zählargumente für die Obergrenze und für „nur Zweierpotenzen“ sind keine Stichproben, sondern Aufzählung, Löser bzw. Beweis.

Abgrenzung: Die Reihe **Koordinationsspiele** (`koordinationsspiel-demo`, `fokalpunkt-demo` u. a.) fragt nach Eigennutz, Gleichgewichten und der Auswahl zwischen ihnen; hier haben alle dasselbe Ziel und es geht um die Strategie bei begrenzter Information. Die Geschwister der Reihe Teamrätsel (Arbeitstitel) heißen `gefangene-kaesten-demo` (Kästen und Zyklen), `informationsleiter-demo` (Stoppen) und `gluehbirne-demo` (Zustand als Kanal), jeweils mit einem anderen Trick; hier ist es der Code. `kasteleyn-demo` enthält das verstümmelte Schachbrett (Domino-Pflasterung), ein anderes Rätsel. **Modelle**: gleichverteilte Hutfarben, Absprache vorab, keine Aussage über Menschen.

## Warum dieses Problem

Fragt man, was eine **abgesprochene Strategie gegenüber dem Raten** bringt, wo die Grenze liegt und wer wen sehen muss, dann liefert dieselbe Idee in vier Gestalten vier Antworten: drei Hüte gewinnen mit Absprache in 75,0 % der Verteilungen statt in 50,0 % (ein Rater allein) oder 12,5 % (alle raten 0), sieben Hüte in 87,5 %, in der Reihe werden alle bis auf einen sicher gerettet, und auf dem Schachbrett kommt ein ganzes Sechs-Bit-Wort durch ein einziges umgedrehtes Feld.

## Kernfrage

*Was bringt die Absprache einer Prüfsumme gegenüber dem Raten, wo liegt eine bewiesene Grenze, und wie hängt der Gewinn davon ab, wer wen sieht?*

## Modell

Alle Hüte sind gleichverteilt und unabhängig. Vier Kulissen:

| Kulisse | Regel | Abgesprochene Prüfsumme | Gewinn |
|---|---|---|---|
| **Hüte gleichzeitig** | n Spieler, 2 Farben, jeder sieht die anderen, sagt gleichzeitig „0“, „1“ oder „passe“ | Syndrom des Hamming-Codes: XOR der Positionen (Spielernummer + 1) mit Hut 1; jeder prüft, ob eine der zwei zu seiner Sicht passenden Verteilungen ein Codewort ist | gewonnen, wenn mindestens einer rät und alle Rater richtig liegen |
| **Hüte in einer Reihe** | n Personen, q Farben, jeder sieht die Hüte vor sich, Tipps von hinten nach vorn, alle hören alle Tipps (aber nicht, ob sie stimmen) | Summe aller Hüte modulo q, von der ersten Person angesagt | Zahl der richtigen Tipps |
| **Summen-Hüte** | n Spieler, q Farben, jeder sieht die anderen, alle tippen gleichzeitig, kein Passen | Summe aller Hüte; Spieler i (i = 0, …, n − 1) hat die Zielsumme i modulo q | gewonnen, wenn mindestens ein Tipp stimmt |
| **Schachbrett** | N = 2^t Felder mit Münzen, A kennt das Schlüsselfeld und dreht genau eine Münze um, B sieht nur das Brett | S = XOR der Nummern der Felder mit Kopf; A dreht Feld S ⊕ Schlüssel | B nennt das Schlüsselfeld |

Die Formeln, die Beweise der Obergrenzen und die Lesehilfe stehen im 📐-Expander der App. Drei Experimente: **E1** zählt alle 3^12 Strategien für drei Hüte, **E2** sucht die beste Strategie für einen Sichtgraphen (jeder sieht nur seine Nachbarn), **E3** zählt perfekte Schachbrett-Strategien für N = 2 und N = 3 und zeigt das Zählargument für „nur Zweierpotenzen“.

## Methodik

* **Hüte gleichzeitig.** Eine Strategie ist zu einer Menge D von „Verlustverteilungen“ gleichwertig: Das Team verliert genau auf D, und eine solche Strategie gibt es genau dann, wenn jede Verteilung in D liegt oder einen Nachbarn (ein Hut anders) in D hat (für jede solche Menge D verliert die folgende Strategie auf genau D, nicht nur höchstens; Test `test_wins_of_losing_set_equal_two_to_n_minus_size_for_dominating_sets`). Die Strategie zu D: Spieler i betrachtet die zwei Verteilungen, die zu seiner Sicht passen; liegt genau eine in D, rät er so, dass seine Verteilung außerhalb von D liegt, sonst passt er. D = Codewörter des Hamming-Codes gibt die Code-Strategie (für n zwischen 2^r − 1 und 2^(r+1) − 2 nutzen nur die ersten 2^r − 1 Spieler den Code, die übrigen passen). Die **beste Strategie** ist die kleinste solche Menge (ein Überdeckungscode vom Radius 1): ein ganzzahliges Überdeckungsmodell (HiGHS, `tools/make_optimum.py`) liefert sie für n = 2 bis 8 vorgerechnet in `data/huete_optimum.json`.
* **Obergrenze.** Bei gleichverteilten Hüten gibt es über alle Verteilungen genauso viele richtige wie falsche Tipps; eine gewonnene Verteilung hat mindestens einen richtigen, eine verlorene höchstens n falsche. Daraus folgt W ≤ n·L und damit ein Gewinnanteil von höchstens n/(n + 1) (ganzzahlig: ⌊n·2^n/(n + 1)⌋ Verteilungen). Bei n = 2^r − 1 erreicht der Hamming-Code sie genau.
* **Reihe.** `play_line` gibt jeder Person nur ihre erlaubten Informationen (Hüte vor ihr, bisherige Tipps); die vektorisierte Fassung rechnet viele Verteilungen auf einmal und wird gegen die Einzelfassung geprüft. Bis 100 000 Verteilungen wird aufgezählt, darüber werden 5 000 Zufallsverteilungen gezogen und als Stichprobe bezeichnet.
* **Summen-Hüte.** Vollständige Aufzählung aller q^n Verteilungen (Maximum 6^7 = 279 936).
* **Schachbrett.** Für N ≤ 16 werden alle 2^N Bretter und alle N Schlüsselfelder wirklich durchgespielt (das Umdrehen wird ausgeführt, S neu berechnet); bei 32 und 64 Feldern sind es 20 000 Zufallsfälle, **nicht aufgezählt**. Für alle N = 2^t beweist die Linearität S(b ⊕ e_j) = S(b) ⊕ j die Strategie.
* **Sichtgraph (E2).** Ganzzahliges Modell (CP-SAT, ein Arbeitsthread, Zeitgrenze 20 s): je Spieler und Sicht genau eine von drei Aktionen, je Verteilung eine Gewinnvariable. Der Status „OPTIMAL“ wird ausgewiesen; bei Zeitgrenze steht „nicht bewiesen“. Die 60 s in den Grenzen sind die Zeitgrenze der Vormessung, nicht die der App.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Aufzählungen oder Beweise, keine Zufallsmessungen, ausgenommen die genannten Stichproben am 64-Felder-Brett und bei den 17 Reihen-Kombinationen mit mehr als 100 000 Verteilungen, und ausgenommen den Wert der besten Strategie bei n = 8 (Löserergebnis, Optimalität in der Testsuite nicht nachgerechnet). Jede steht in `tests/test_claims.py` bzw. in den Orakel-Tests (`tests/test_oracle_codes_strategie.py`).

| Frage | Befund | Test |
|---|---|---|
| Gewinnt für **drei Hüte** irgendeine Strategie mehr als 75,0 %? | **Nein.** Von allen 531 441 Strategien (3^12; je Spieler und Sicht „0“, „1“ oder „passe“) gewinnt keine in mehr als **6 von 8** Hutverteilungen (75,0 %); genau 4 Strategien erreichen das, 26 550 gewinnen mindestens 4 von 8. Zahl der Strategien nach Gewinnzahl 0 bis 8: 16 335; 120 736; 228 780; 139 040; 25 922; 624; 4; 0; 0. | `test_claim_three_players_all_531441_strategies` |
| Wie hoch ist die **Obergrenze** je Spielerzahl? | Keine Strategie gewinnt in mehr als ⌊n·2^n/(n + 1)⌋ Verteilungen: **2, 6, 12, 26, 54, 112, 227** für n = 2 bis 8 (bewiesen durch Zählen; für n = 3 durch die Aufzählung bestätigt). Bei zwei Farben und gleichverteilten Hüten. | `test_claim_table_bound_code_and_best_for_two_to_eight_players`, `test_claim_counting_bound_argument_by_enumeration_for_three_players` |
| Was gewinnen **Code-Strategie** und **beste Strategie**? | Code-Strategie: **2, 6, 12, 24, 48, 112, 224**; beste Strategie (kleinste dominierende Menge, HiGHS): **2, 6, 12, 25, 52, 112, 224** von 4, 8, 16, 32, 64, 128, 256 für n = 2 bis 8. | `test_claim_table_bound_code_and_best_for_two_to_eight_players`, `test_claim_optimum_sizes_of_dominating_sets` |
| Ist der Code immer der Beste? | **Nein, nicht für alle Größen.** Bei n = 5 gewinnt die beste Strategie 25 von 32 (78,1 %) gegen 24 von 32 (75,0 %) des Codes, bei n = 6 gewinnt sie 52 von 64 (81,2 %) gegen 48 von 64 (75,0 %); in den übrigen **fünf** der sieben Größen (n = 2, 3, 4, 7, 8) sind beide gleich. Die Obergrenze 26 bzw. 54 ist dort nicht erreicht, bei n = 2, 3, 4, 7 ist sie von der besten Strategie erreicht, bei n = 8 nicht (224 gegen 227). | `test_claim_best_beats_code_in_exactly_two_of_seven_sizes_with_the_stated_percentages`, `test_claim_the_integer_bound_is_reached_at_n_2_3_4_7_and_missed_at_5_6_8` |
| Wann ist der Code **perfekt**? | Bei n = 3 und n = 7: **6 von 8 (75,0 %)** und **112 von 128 (87,5 %)**, genau die Obergrenze. Bei n = 8 sind es 224 von 256, die Obergrenze 227 ist nicht erreicht (ein Spieler passt immer). | `test_claim_hamming_codes_are_perfect_for_three_and_seven_players` |
| Und **ohne Code**? | Ein einzelner Rater (die anderen passen) gewinnt für n = 2 bis 8 genau **die Hälfte** der Verteilungen; sagen alle „0“, gewinnt das Team nur bei lauter Nullen (**1** von 2^n). | `test_claim_overview_comparison_with_single_guesser_and_everyone_guessing` |
| Wie viele sind in der **Reihe** sicher gerettet? | In **allen 38** der 55 Kombinationen von n = 2 … 12 und q = 2 … 6, die aufgezählt werden (q^n ≤ 100 000), liegen mindestens **n − 1** Personen richtig und im Mittel genau **n − 1 + 1/q**. Beispiel n = 12, q = 2 (alle 4 096 Verteilungen): mindestens 11, im Mittel 11,50 gegen 6,00 ohne Plan. Die verbleibenden 17 Kombinationen sind Stichproben (5 000 Verteilungen), für sie gilt n − 1 als Beweis, nicht als Messung. Die erste Person liegt in 1/q der Fälle richtig. | `test_claim_line_all_enumerated_combinations_give_n_minus_one_and_the_mean`, `test_claim_line_example_twelve_persons_two_colors`, `test_claim_line_first_person_is_right_in_one_over_q_of_all_distributions` |
| Geht in der Reihe **mehr**? | Nein, für die kleinsten Fälle ausgezählt: Aus **allen** Strategien für (n, q) = (2, 2), (3, 2), (2, 3) ist der beste schlechteste Fall n − 1 und das beste Mittel n − 1 + 1/q. Allgemein: Für jede Sicht der ersten Person gibt es eine Farbe, bei der sie falsch liegt, und im Mittel liegt sie mit 1/q richtig. | `test_no_line_strategy_beats_the_sum_announcement` (Orakel) |
| **Summen-Hüte**: wie viele Tipps stimmen? | Bei **n = q** (q = 2 … 6) stimmt in allen q^q Verteilungen **genau ein** Tipp. Raten ohne Plan gewinnt dagegen bei q = n = 3 nur in 70,4 % und bei q = n = 6 in 66,5 % der Verteilungen (1 − (1 − 1/q)^n; für n = q und wachsendes q nähert sich das 1 − 1/e = 63,2 %). Bei mehr Spielern als Farben stimmt mindestens ein Tipp, bei weniger ist der Gewinnanteil n/q: für n = 3, q = 5 genau 75 von 125 = 60,0 %. | `test_claim_sums_exactly_one_right_for_n_equals_q_two_to_six`, `test_claim_sums_chance_values_and_the_limit`, `test_claim_sums_three_players_five_colors` |
| Ist n/q für **Summen-Hüte** eine Grenze? | Ja: Aus **allen** Strategien für (n, q) = (1, 2), (1, 3), (2, 2), (2, 3), (2, 4), (3, 2) ist die beste Gewinnzahl min(1, n/q)·q^n. Beweis: Der Erwartungswert der Zahl richtiger Tipps ist n/q, der Gewinnanteil höchstens so groß. | `test_no_strategy_beats_the_bound_min_one_n_over_q` (Orakel) |
| **Schachbrett**: stimmt die XOR-Strategie? | Für N = 2, 4, 8 und 16 Felder sind **alle** 2^N Bretter mit allen N Schlüsselfeldern durchgespielt: 8, 64, 2 048 und 1 048 576 Fälle, **0 Fehler**. Für 64 Felder: 20 000 Zufallsfälle, 0 Fehler, **nicht aufgezählt** (64 · 2^64 Fälle); dass es immer gilt, folgt aus S(b ⊕ e_j) = S(b) ⊕ j. | `test_claim_board_exhaustive_case_counts`, `test_claim_board_sixty_four_is_a_sample_of_twenty_thousand`, `test_flipping_field_j_changes_the_code_by_exactly_j_on_random_boards` |
| Gibt es das auch für **3 oder 6 Felder**? | **Nein.** Eine perfekte Strategie färbt die 2^N Bretter mit N Farben so, dass die N Nachbarn jedes Bretts alle Farben tragen; dann hat jede Farbklasse 2^N/N Bretter, also muss N ein Teiler von 2^N sein. Aufgezählt: für N = 2 gibt es 4 solche Strategien, für N = 3 gibt es **0** (alle 6 561 Färbungen geprüft). Das Zählargument lässt zwischen N = 2 und N = 16 genau 2, 4, 8, 16 zu; für N = 2 bis 7 bestätigt ein ganzzahliges Modell (CP-SAT): möglich für 2 und 4, unmöglich für 3, 5, 6 und 7. | `test_claim_board_only_powers_of_two_by_enumeration_and_counting`, `test_perfect_strategy_exists_exactly_for_powers_of_two_up_to_seven` (Orakel) |
| **Wer sieht wen?** (E2) | Beste Strategie (CP-SAT, jeweils als optimal bewiesen) bei „Jeder sieht jeden“: **6, 12, 25** Gewinnverteilungen von 8, 16, 32 für n = 3, 4, 5; im Ring **6**, **8**, **16** (n = 3 ist ein Dreieck, n = 4 und 5 sind es nicht), in der Kette und im Stern **4, 8, 16** für n = 3, 4, 5. In allen **8** gemessenen Graphen ohne Dreieck (Ring n = 4, 5; Kette und Stern n = 3, 4, 5) ist der Optimalwert genau **1/2**; mit einem Dreieck sind es mindestens 3/4 (Beweis: die drei spielen die Strategie für drei Hüte, den Hamming-Code der Länge 3, alle anderen passen). Für größere Graphen und andere Sichtgraphen als diese vier Formen ist das **nicht** gemessen. | `test_claim_graph_values_for_three_to_five_players`, `test_claim_graphs_without_triangle_are_at_one_half_and_with_triangle_at_least_three_quarters`, `test_claim_embedding_a_triangle_gives_three_quarters_in_any_graph` |

Die Zahl 6 von 8 bei drei Hüten und 112 von 128 bei sieben Hüten sind bekannt (die Hamming-Strategie ist Lehrbuch); die Tabelle für n = 2 bis 8 samt der Beobachtung, dass der Code bei n = 5 und n = 6 nicht der Beste ist, ist hier selbst ausgezählt. Die Strategien entsprechen Überdeckungscodes vom Radius 1 (siehe Quellen); deren Tabellen wurden nicht eingesehen, die Werte sind in der Theorie vermutlich bekannt.

## Ehrliche Grenzen

* **Gleichverteilte, unabhängige Hüte** und eine Gewinnregel „mindestens ein Rater, alle Rater richtig“. Bei anderer Verteilung oder anderer Gewinnregel (z. B. alle müssen raten und richtig liegen; so ist es nach dem Gedächtnis bei Riis, ungeprüft) gelten die Zahlen nicht.
* **Zwei Farben bei Hüte gleichzeitig.** Für q Farben gibt es Überdeckungsverfahren (Lenstra und Seroussi, „strong coverings“, laut Zusammenfassung); hier nicht gerechnet.
* **Die Obergrenze ⌊n·2^n/(n + 1)⌋ ist von der besten Strategie bei n = 2, 3, 4 und 7 erreicht, bei n = 5, 6 und 8 nicht**; der Anteil n/(n + 1) selbst wird nur bei n = 2^r − 1 (hier 3 und 7) genau getroffen. Die beste Strategie ist für n ≤ 8 aus einem Löser (HiGHS, „Optimal“); für n = 8 ist die Optimalität in der Testsuite **nicht** nachgerechnet (n ≤ 7 wird neu gelöst, n ≤ 4 zusätzlich durch Aufzählung aller Teilmengen).
* **Die Reihe** gilt für fehlerfreie Rechnung aller Beteiligten; ein einziger Fehler macht alle Folgenden falsch (folgt aus der Formel, nicht gemessen). Bei den 17 Kombinationen mit Stichprobe ist „n − 1“ ein Beweis, die Stichprobe zeigt es nur.
* **Das 64-Felder-Brett** ist eine Stichprobe mit 20 000 Fällen; die vollständige Prüfung geht nur bis 16 Felder (1 048 576 Fälle).
* **Sichtgraphen** nur für höchstens fünf Spieler und vier Formen; ab sechs Spielern konnte der Löser in 60 s nicht immer beweisen (Vormessung `teamraetsel-planung/vormessung/out_e2_cpsat_huete.txt`: von 8 Graphen mit 6 oder 7 Spielern bewies er in 1 Fall die Optimalität).
* Die Rätsel sind **Modelle**. Aussagen über das Verhalten von Menschen gehören nicht dazu.

## Verifikation

* **Kern:** jede Einheit gegen Handrechnung auf Mini-Instanzen (`tests/conftest.py`, `tests/test_hats.py`, `tests/test_line_sums_board.py`); die Strategien lesen nur die Hüte der anderen (Test: eigener Hut ändern ändert die Aktion nicht); Zweig-Test: „beste Strategie“ weicht vom Code genau bei n = 5 und 6 ab.
* **Orakel** (`tests/test_oracle_codes_strategie.py`, anderer Rechenweg): Hamming-Regel als Schleife mit Parity-Check-Matrix gegen die XOR-Fassung für n = 2 bis 8 und alle Verteilungen; Stichprobe aus allen 3^12 Strategien in Schleifen gegen die vektorisierte Aufzählung; das Optimum als CP-SAT-Strategiemodell (n = 2 bis 5, anderes Modell als die dominierende Menge) und als HiGHS-Überdeckungsmodell (n = 2 bis 7); n ≤ 4 durch Aufzählung aller Teilmengen; Reihe und Summen-Hüte durch Aufzählung aller Strategien in kleinen Fällen; Schachbrett als Schleife bis 8 Felder und als CP-SAT-Färbungsmodell; Sichtgraph als Schleife (Kette und Stern bei drei Spielern), vektorisierte Aufzählung (Dreieck, Kette bei vier Spielern) und Löser.
* **Zahlen:** jede Befundzahl dieser README in `tests/test_claims.py` bzw. in den Orakel-Tests (ausgenommen die Optimalität bei n = 8, siehe Grenzen); Verdikte als reine Funktionen in `tests/test_verdicts.py` (jede Schwelle, jede Zahl im Text, auch der Fehlerzweig „über dem Optimum“).
* **Eigenschaften** (`tests/test_eigenschaften_codes_strategie.py`): Umnummerieren der Spieler, Vertauschen beider Farben, Monotonie in n, Verschiebung der Zielsummen, die Lemma-Zeile des Schachbretts, gleiche Ausgabe in zwei Prozessen mit anderer Hash-Randomisierung.
* **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Inhaltstests je Kulisse und je Strategie, Layout (Schnellstart oben, aktives Preset hervorgehoben, jeder Regler in `SETTING_SPECS`), Footer.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: vier Kulissen, drei Experimente, Grenzen, Mathematik, PDF |
| `cod_hats.py` | Kern Hüte gleichzeitig: Syndrom, Strategie aus einer Verlustmenge, Ergebnisse, Obergrenze, Aufzählung aller Strategien bei drei Spielern |
| `cod_line.py` | Kern Reihe: Tipps der ersten und der späteren Personen, vektorisierte Fassung |
| `cod_sums.py` | Kern Summen-Hüte: Zielsummen, Tipps, Aufzählung |
| `cod_board.py` | Kern Schachbrett: Code S, Umdrehen, vollständige und stichprobenhafte Prüfung, Färbungen |
| `cod_graph.py` | Sichtgraphen, Strategietabellen, Aufzählung, ganzzahliges Modell (CP-SAT) |
| `cod_evaluation.py` | Einstellungen, Szenen, Kennzahlen, Verdikte (reine Funktionen) |
| `cod_experiments.py` | E1, E2, E3 und ihre Verdikte |
| `cod_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `cod_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `cod_layout.py` | Fester Kopf (Stylesheet) |
| `cod_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `cod_pdf_export.py` | PDF-Export (fpdf2), erst nach Klick |
| `data/huete_optimum.json` | Vorgerechnete kleinste dominierende Mengen für n = 2 bis 8 |
| `tools/make_optimum.py` | Reproduktionsskript für die Datei (HiGHS) |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Orakel, Claims, Verdikte, Eigenschaften, Randfälle, Abbildungen, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

* **Hüte gleichzeitig mit q > 2 Farben** und **gemischte Strategien** (gemeinsamer Zufall ist eine Mischung deterministischer Strategien und kann den besten deterministischen Wert nicht übertreffen, aber die Demo zeigt ihn nicht).
* **Ungleiche Hutverteilungen** und die **Gewinnregel „alle raten“** (Hut-Zahl von Graphen, Riis; die Regel dort ist ungeprüft).
* **Sichtgraphen ab sechs Spielern** und beliebige Graphen: der Löser beweist die Optimalität dort nicht in vertretbarer Zeit (siehe Grenzen).
* **Bester Erfolg auf Brettern, die keine Zweierpotenz sind** (wie nahe man bei 3 oder 6 Feldern an „immer“ kommt): nicht gerechnet.
* **Die Website-Einbindung** (Karte, Konzepte-Linie): offen, braucht die Linienspezifikation `teamraetsel` (`WEBSITE-PLAYBOOK.md`). Die Erklärseite „verständlich erklärt“ gibt es als `huete-raetsel-erklaert.html` auf der Website; die App verlinkt sie im Expander „💬 In einfachen Worten“.

## Quellen (nur geprüft, was hier steht)

* Lenstra, H. W.; Seroussi, G.: *On Hats and other Covers* (arXiv cs/0509045, 2005). Laut Zusammenfassung: Bei zwei Farben entsprechen die Strategien dem Überdeckungscode vom Radius 1; der Zusammenhang mit Hamming-Codes für n = 2^m − 1 war schon vorher bekannt.
* Riis, S.: *Information flows, graphs and their guessing numbers* (Electronic Journal of Combinatorics 14 (2007), R44): Rateaufgaben auf Graphen (nur Titel und bibliografische Angabe wurden geprüft; dass dort alle Rater richtig liegen müssen, ist die Erinnerung, nicht geprüft).
* Die Hüte in der Reihe, die Summen-Hüte und das Schachbrett gelten als **Sammlungswissen ohne einzelne Quelle** (ungeprüft); die Herkunft des Hut-Rätsels bei Ebert (1998) steht nur in Sekundärquellen und wird nicht als geprüft ausgegeben.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die Python-Version der Streamlit Cloud ist in den App-Einstellungen zu wählen (Tests laufen in der CI mit 3.12; die Demo nutzt nur Merkmale, die dort laufen). <!-- lint-ok: dezimalpunkt -->

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Die Suite hat **180 Tests**.

Gebaut mit Streamlit, Plotly, NumPy, pandas, OR-Tools und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Teamrätsel: Strategie ohne Verständigung](https://sebastianhanisch.net/konzepte-teamraetsel.html).
