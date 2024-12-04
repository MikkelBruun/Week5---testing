# Rettelser

Opdateret requirements.txt så det inkluderer alle dependencies. Inklusiv xlsxwriter, som teoretisk set er optional, men er nødvendig i dette projekt for at åbne excel filer.

For at køre kræver programmet en mappe med en input fil "customer_data\GRI_2017_2020.xlsx". Uden denne kører programmet ikke. README nævner at man kan override en række default filstier, men nævner ikke hvad disse er.

Har tilføjet et optional arg til `File_Handler.start_download`: `max_rows=20`. Som udleveret havde programmet en lignende hardcoded grænse, men det kan nu sættes efter behov.
