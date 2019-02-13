#!/bin/bash
source /root/politiqueJournalNpl/.politiqueJournalNpl/bin/activate
python /root/politiqueJournalNpl/scrpy.py --path=/root/renminRibao/txt/
python /root/politiqueJournalNpl/scrpyPdf.py --path=/root/renminRibao/pdf/
deactivate
