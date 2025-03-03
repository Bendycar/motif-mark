#!/usr/bin/env python
import argparse
import cairo
import re 

def get_args():
    parser = argparse.ArgumentParser(description="Python program to visualize FASTA file and annotate with Motif file")
    parser.add_argument("-f", help="Path to FASTA file of interest", type = str, required = True)
    parser.add_argument("-m", help="Path to motifs file", type = str, required = True)

    return parser.parse_args()

IUPAC_codes = {'A':'[Aa]', 'C': '[Cc]','G':'[Gg]','T':'[Tt]','U':'[Uu]', 'R':'[AGag]','Y':'[CTct]','S':'[GCgc]','W':'[ATat]','K':'[GTgt]','M':'[ACac]','B':'[CGTcgt]','D':'[AGTagt]','H':'[ACTact]','V':'[ACGacg]','N':'[ACTGactg]',
               'a':'[Aa]', 'c': '[Cc]','g':'[Gg]','t':'[Tt]','u':'[Uu]', 'r':'[AGag]','y':'[CTct]','s':'[GCgc]','w':'[ATat]','k':'[GTgt]','m':'[ACac]','b':'[CGTcgt]','d':'[AGTagt]','h':'[ACTact]','v':'[ACGacg]','n':'[ACTGactg]'
               }

class Motif:
    def __init__(self, start, length, color):
        self.start = start
        self.length = length
        self.color = color
    
    def draw_line(self):
        pass


class FastaRecord:
    def __init__(self, gene, seq, RC: bool):
        self.gene = gene
        self.seq = seq
        self.RC = RC
        self.start, self.end = self.find_exon(seq)


        self.motif_list = self.find_motifs(seq, motif_dict)
        self.length = len(seq)
    
    def __repr__(self):
        return f"motifs: {self.motif_list}"#f"FASTA record with gene {self.gene} and sequence {self.seq} (Reverse complemented: {self.RC})"
    
    def find_motifs(self, seq, motif_dict):
        motifs = []
        for regex in motif_dict.values():
            matches = re.findall(regex, seq)
            for match in matches:
                motifs.append(match)
        return motifs


    def find_exon(self, seq):
        exon = re.search(r'[A-Z]+', seq)
        if exon:
            start = exon.start() # Returns 0-indexed start position of matching group
            end = exon.end()
        return (start + 1, end) # I want to use 1-based indexing

def generate_regex(motif: str) -> str:
    regex = ""
    for char in motif:
        regex = regex + IUPAC_codes[char]
    return regex

def generate_motif_dict(motifpath: str) -> dict: 
    motifs = {}
    with open(motifpath, "r") as fh:
        for motif in fh:
            motif = motif.strip()
            if motif:
                motif_regex = generate_regex(motif)
                motifs[motif] = motif_regex
                print(motif)
                print(motifs[motif])
    return motifs
        

def generate_colors(motiflist):
    pass

def parse_fasta(fastapath: str) -> list:
    fasta_list = []
    seq = ""
    gene = None
    with open(fastapath, "r") as fh:
        for line in fh:
            if line.startswith('>'):
                if gene: #Should only not happen the first line, where gene will be None
                    record = FastaRecord(gene,seq,RC)#After that, every time a header will be encountered the record will be written
                    fasta_list.append(record)
                gene = re.match(r">(\S+)", line).group(1) # Literal > followed by any number of non-whitespace characters
                rev_comp = "reverse complement" in line.lower() 
                RC = bool(rev_comp) #Establishing values for next record
                seq = "" #Initializing empty string
            seq += line
    record = FastaRecord(gene,seq,RC)
    fasta_list.append(record)
    return fasta_list

def final_drawing():
    pass

if __name__ == "__main__":

    args = get_args() 
    fasta = args.f
    motif_file = args.m
    motif_dict = generate_motif_dict(motif_file)
    fasta_list = parse_fasta(fasta)

    #key = generate_colors(motif_list)

