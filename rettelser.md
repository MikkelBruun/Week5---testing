# Rettelser

Rettelser i kode er generelt markeret med `## Rettelse`, hvis der er tale om en enkelt linje:

```python
if downloaded:
    finished_dict[name]="yes" ## RETTELSE
else:
    finished_dict[name]="no" ## RETTELSE
```

Hvis der er en blok af rettelse er den afgrænset med `## RETTELSE` og `## /RETTELSE`:

```python
## RETTELSE
#finished_data_frame = pl.from_dict(finished_dict)
_finished_dict = {ID: [key for key in finished_dict], "pdf_downloaded": [finished_dict[key] for key in finished_dict]}
finished_data_frame = pl.from_dict(_finished_dict)
## /RETTELSE
```

## At køre programmet

For at køre kræver programmet en mappe med en input fil "customer_data\GRI_2017_2020.xlsx". Uden denne kører programmet ikke. README nævner at man kan override en række default filstier, men nævner ikke hvad disse er.

Jeg har pdateret requirements.txt så det inkluderer alle dependencies. Inklusiv xlsxwriter, som teoretisk set er optional, men er nødvendig i dette projekt for at åbne excel filer.

Til at starte med var der en hardcoded begrænsning på 20 downloads. Nu har jeg tilføjet et optional arg til `File_Handler.start_download`: `max_rows=20`.

## Fundne fejl

Integrationtests `test_meta_yes_in_files` og `test_meta_no_not_in_files` viste at der ikke var sammenhæng mellem hvad der blev skrevet i metafilen, og hvilke downloads var successfulde. I download_thread bliver der tilføjet til to lister, `ID` og `pdf_downloaded` ("yes"/"no"). Problemet var at filens id blev tilføjet ved download start, og "yes/no" blev tilføjet i slutningen (racecondition). Dette blev løst ved at skrive dem samtidig som key/val i en dict.
