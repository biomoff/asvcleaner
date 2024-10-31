import Bio.Seq as Seq
import Bio.SeqRecord as SeqRecord
from Bio import SeqIO
import subprocess
import os
import argparse

parser = argparse.ArgumentParser(description="Program for removing sequences from multi-record fasta files that do not match a database")
parser.add_argument("-in", "--input", help= ".fasta input file to be cleaned")
parser.add_argument("-db", "--database", help= "name / path of database file generated with 'makeblastdb' in BLAST+")
parser.add_argument("-t","--seqtable", help= "file name of the sequence table (in tsv format) you want to non-matching ASVs to be removed from; ASV names must be in column called 'ASV_ID'")
parser.add_argument("--taxtable", help= "file name of the taxonomy table (in tsv format) you want to non-matching ASVs to be removed from; ASV names must be in column called 'ASV_ID'")
parser.add_argument("--speciestable", help= "file name of the species table from dada2 species assignment (in tsv format) you want to non-matching ASVs to be removed from; ASV names must be in column called 'ASV_ID'")
parser.add_argument("--evalue", default= 10, help= "E-value to use in Blastn search")

# Assign input variables
args = parser.parse_args()
db = args.database
infile = args.input
seqtable = args.seqtable
taxtable = args.taxtable
speciestable = args.speciestable
evalue = args.evalue

if seqtable:
    import pandas as pd


def main():
    
    # Check for input
    if infile == None:
        raise SystemExit("No input provided!")
    
    # Create directory for temporary files
    try:
        os.mkdir(path= 'temporary')
    except FileExistsError:
        raise SystemExit("Directory: 'temporary' already exists, please rename it or remove it prior to rerunning")

    print(f"Using database: {db}")

    # Create directory for cleaned output files
    try:
        os.mkdir(path= "cleaned")
    except FileExistsError:
        raise SystemExit("Directory: 'cleaned' already exists, please ranem it or remove it prior to rerunning")


    # open files for output
    rejected = open('cleaned/rejected.seqs.fasta','w')
    rejectedlist = open('cleaned/rejected_ASVs.txt','w+')
    accepted = open('cleaned/cleaned.seqs.fasta','w')
    acceptedlist = open('cleaned/cleaned_ASVs.txt','w')

    # Read in sequences as alignment
    records = SeqIO.parse(infile, format= 'fasta')

    # for loop iterating through all sequences
    command = f"grep '>' {infile} | wc -l"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    total = int(stdout.strip())
    rejected_asvs = []

    for index,record in enumerate(records):
        # counter        
        if index % 100 == 0:
            print(f"Progress: {round((index/total)*100)}%", end= "\r")

        # create fasta file for the record
        with open(f"temporary/{record.id}.fasta",'w') as f:
            f.write(f">{record.id}\n{record.seq}")

        # run blast against database
        command = F"blastn -db {db} -query temporary/{record.id}.fasta -evalue {evalue} -out temporary/{record.id}.out"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # exit if BLAST search fails
        if process.returncode != 0:
            raise SystemExit("BLAST search failed")


        # check for matches
        with open(f"temporary/{record.id}.out",'r') as out:
            result = out.read()

        if "No hits found" in result:
            rejected.write(f">{record.id}\n{record.seq}\n")
            rejectedlist.write(f"{record.id}\n")
            rejected_asvs.append(record.id)
            print(f"{record.id} was rejected due to no match in the database")
        else:
            accepted.write(f">{record.id}\n{record.seq}\n")
            acceptedlist.write(f"{record.id}\n")

        # remove record's temporary files
        command = f"rm temporary/{record.id}.out temporary/{record.id}.fasta"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    # clean sequence table
    if seqtable != None:
        print(f"Cleaning sequence table '{seqtable}'")
        df = pd.read_csv(seqtable, sep = '\t')
        filter = [asv for asv in rejected_asvs]
        filtered = df[df['ASV_ID'].isin(filter) == False]
        filtered.to_csv('cleaned/cleaned_ASV_table.tsv', sep= '\t', index= False)
        print("Done.")

    if taxtable != None:
        print(f"Cleaning taxonomy table '{taxtable}'")
        df= pd.read_csv(taxtable, sep= '\t')
        filter = [asv for asv in rejected_asvs]
        filtered = df[df['ASV_ID'].isin(filter) == False]
        filtered.to_csv('cleaned/cleaned_tax_table.tsv', sep= '\t', index= False)
        print("Done.")

    if speciestable != None:
        print(f"Cleaning species table '{speciestable}'")
        df= pd.read_csv(speciestable, sep= '\t')
        filter = [asv for asv in rejected_asvs]
        filtered = df[df['ASV_ID'].isin(filter) == False]
        filtered.to_csv('cleaned/cleaned_species_table.tsv', sep= '\t', index= False)
        print("Done.")

    # close files
    rejected.close()
    rejectedlist.close()
    accepted.close()
    acceptedlist.close()

    # remove temporary directory
    command = "rm -r temporary"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()


if __name__ == "__main__":
    main()
