# Summary

I made this program to remove sequences from the all.seqs.fasta output of dada2 and dadasnake that do not have any homology to a set of reference sequences (a BLAST database formatted by makeblastdb in BLAST+). These databases can easily be made by installing BLAST+ (which is easiest using conda: "conda install blast") and then using

`makeblastdb -in <multirecord.fasta> -input_type 'fasta' -dbtype 'nucl' -out <database-name>`

**Note: blast is provided in the 'bio' conda environment.**

# Running asvcleaner

All you need to supply to asvcleaner is a multi-record fasta file (e.g. all.seqs.fasta) and a database. This program can be called using:

`python3 path/to/asvcleaner.py -in <all.seqs.fasta> -db /path/to/database/<database-name>`


You may need to specify the full path to the database you generated. E.g.

`python3 path/to/asvcleaner.py -in <all.seqs.fasta> -db /path/to/database/<database-name>/<database-name>`

# Dependencies

asvcleaner depends on biopython, pandas, and argparse; these are provided in the supplied conda environments, along with blast.


# Output

All output files go to a `cleaned` subdirectory Output includes a list of ASVs that were rejected (rejected_ASVs.txt) and a list of ASVs that passed the filter (cleaned_ASVs.txt), Fasta format sequence files for cleaned (cleaned.seqs.fasta) and rejected ASVs (rejected.seqs.fasta), a cleaned sequence table (cleaned_ASV_table.tsv), and cleaned taxonomy (cleaned_tax_table.tsv) and species (cleaned_species_table.tsv) tables.
