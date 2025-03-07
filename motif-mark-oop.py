#!/usr/bin/env python
import argparse
import cairo
import re 
import random 

def get_args():
    parser = argparse.ArgumentParser(description="Python program to visualize FASTA file and annotate with Motif file")
    parser.add_argument("-f", help="Path to FASTA file of interest", type = str, required = True)
    parser.add_argument("-m", help="Path to motifs file", type = str, required = True)

    return parser.parse_args()

## International Union of Pure and Applied Chemistry codes allow for symbols such as "Y" to represent ambiguous nucleotides such as "C or T". 
## This uses Regex equivalent of the ambiguous nucleotides to create a search for motifs with IUPAC symbols in them
IUPAC_codes = {'A':'[Aa]', 'C': '[Cc]','G':'[Gg]','T':'[Tt]','U':'[Tt]', 'R':'[AGag]','Y':'[CTct]','S':'[GCgc]','W':'[ATat]','K':'[GTgt]','M':'[ACac]','B':'[CGTcgt]','D':'[AGTagt]','H':'[ACTact]','V':'[ACGacg]','N':'[ACTGactg]',
               'a':'[Aa]', 'c': '[Cc]','g':'[Gg]','t':'[Tt]','u':'[Tt]', 'r':'[AGag]','y':'[CTct]','s':'[GCgc]','w':'[ATat]','k':'[GTgt]','m':'[ACac]','b':'[CGTcgt]','d':'[AGTagt]','h':'[ACTact]','v':'[ACGacg]','n':'[ACTGactg]'
               }

class Motif:
    '''Each individual instance of a motif creates a motif object. 
    
    Attributes: 
        Start: Starting position of the motif
        Stop: End position of the motif
        Seq: The original sequence in the motif file, containing the IUPAC codes
        Color: Randomly assigned color, unique to each motif sequence
        Order: Order of the FASTA file that the motif is found in. Used for y-coordinate while drawing
    
    Methods:
        draw_motif: Draws motif on corresponding FASTA visualization
    '''
    def __init__(self, seq, start, stop, order):
        self.start = start
        self.stop = stop
        self.seq = seq
        self.order = order
        self.color = color_dict[seq]
        self.red, self.green, self.blue = self.color 
    
    def draw_motif(self, context):
        context.set_source_rgb(self.red, self.green, self.blue) # Unique color from motif_dict
        context.set_line_width(40)
        context.move_to(self.start + 100, 200 * self.order) # (x, y)
        context.line_to(self.stop + 100, 200 * self.order)
        context.stroke()

        

class FastaRecord:
    '''FASTA record that will be visualized with motifs
    Attributes:
        Gene: Just the gene name, extracted from record header
        Seq: Full FASTA sequence
        RC: Bool RC, based on "(reverse complement)" in record header
        Order: Order of appearence in FASTA file. Used for y-coordinate in drawing
        Start: Exon start position
        End: Exon end position
        Motif_list: All motifs that appear in the record
        Length: Length of full record sequence
    
    Methods:
        find_motifs: Uses Regex to find all instances of motifs in record, creating unique object for each motif found
        find_exon: Uses Regex to find start and stop position of the one and only one exon in each gene
        draw: Creates visualization of gene, exon, and every motif in motif_list
    '''
    def __init__(self, gene, order, seq, RC: bool):
        self.gene = gene
        self.seq = seq
        self.RC = RC
        self.order = order
        self.start, self.end = self.find_exon(seq)
        self.motif_list = self.find_motifs(seq, motif_dict)
        self.length = len(seq)
     
    def find_motifs(self, seq: str, motif_dict: dict) -> list:
        motifs = [] # List of motif objects for each instance of a motif in the FASTA record
        for motif, regex in motif_dict.items(): # Motif_dict contains Regex equivalent of all motif sequences, accounting for IUPAC codes
            matches = re.finditer(regex, seq)
            for match in matches:
                motifs.append(Motif(motif, match.start() + 1, match.end(), self.order)) # 1-based index of motif start and stop point
        return motifs

    def find_exon(self, seq: str) -> tuple[int, int]:
        exon = re.search(r'[A-Z]+', seq) # Contiguous sequence of all capital letters denotes exon -- problem specification states one and only one exon per FASTA record
        if exon:
            start = exon.start() # Returns 0-indexed start position of matching group
            end = exon.end()
        else:
            raise Exception("Records must have contain exactly one exon")
        return (start + 1, end) # I want to use 1-based indexing
    
    def draw(self, context):
        ## Drawing black line for entire gene
        context.set_source_rgb(0, 0, 0) # RBG code for black
        context.set_line_width(2)
        context.move_to(100, 200 * self.order)  #(x,y)
        context.line_to(self.length + 100, 200 * self.order)
        context.stroke()

        ## Drawing black box for exon
        context.set_source_rgb(0,0,0)
        context.set_line_width(30)
        context.move_to(self.start + 100, 200 * self.order)
        context.line_to(self.end + 100, 200 * self.order)
        context.stroke()
        
        ## Drawing gene label
        context.set_source_rgba(0, 0, 0, 1)
        context.set_font_size(25) 
        context.move_to(50, 200 * self.order - 50)
        context.show_text(f"Gene: {self.gene}")

        ## Drawing all motifs for FASTA record
        for motif in self.motif_list:
            motif.draw_motif(context)


def generate_regex(motif: str) -> str:
    '''Uses IUPAC codes dictionary to create Regex equivalent of each motif'''
    regex = ""
    for char in motif:
        regex = regex + IUPAC_codes[char]
    return regex

def generate_motif_dict(motifpath: str) -> dict: 
    '''Creates dictionary for all motif sequences containing Regex equivalents'''
    motifs = {}
    with open(motifpath, "r") as fh:
        for motif in fh:
            motif = motif.strip()
            if motif:
                motif_regex = generate_regex(motif)
                motifs[motif] = motif_regex
    return motifs
        
def generate_colors(motiflist: dict) -> dict:
    '''Returns randomly selected red, green, and blue values that are at least 32 apart for at least one element on the 0-256 scale'''
    random.seed(1738)
    colors_dict = {}
    options = range(0,256,32) # All generated values must be at least 32 away on at least one element of the RGB scale in order to appear distinct
    for motif in motiflist:
        red, green, blue = random.sample(options, 3) # Sampling from colors without replacement to ensure no repeats
        red, green, blue = red / 256, green / 256, blue / 256 # PyCairo wants colors between 0-1, not 0-256
        colors_dict[motif] = (red, green, blue)
    return colors_dict

def parse_fasta(fastapath: str) -> list:
    '''Processes FASTA file and returns list of FASTA objects. Extracts gene, sequence, order, and RC bool contained within FASTA object'''
    fasta_list = []
    seq = ""
    gene = None
    order = 0
    with open(fastapath, "r") as fh:
        for line in fh:
            if line.startswith('>'): # Only header lines begin with >
                if gene: # Should only not happen the first line, where gene will be None
                    order += 1
                    record = FastaRecord(gene,order,seq,RC) # After that, every time a header is encountered the record will be written
                    fasta_list.append(record)
                gene = re.match(r">(\S+)", line).group(1) # Literal > followed by any number of non-whitespace characters
                rev_comp = "reverse complement" in line.lower() 
                RC = bool(rev_comp) # Establishing values for next record
                seq = "" # Initializing empty string for next record
            else:
                seq += line.strip() # Adding every non-header line to the sequence string
    # Adding final record
    order += 1 
    record = FastaRecord(gene,order,seq,RC)
    fasta_list.append(record)
    return fasta_list

def final_drawing(fasta_list: list, filename: str):
    '''Creates surface, context, title, key, and calls draw method on all FASTA objects.''' 
    ## File sizing
    width = 1100 # Hard coded because we know no sequences are longer than 1000
    height = len(fasta_list) * 200 + len(motif_dict) * 70 # Account for number of genes and size of key
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    context = cairo.Context(surface)

    ## White background
    context.set_source_rgb(1, 1, 1)
    context.rectangle(0, 0, width, height)
    context.fill()
    
    ## Title
    context.set_source_rgba(0, 0, 0, 1)
    context.set_font_size(40) 
    context.move_to(450, 80)
    context.show_text("Motif Mark") 

    ## Drawing all FASTAs and motifs
    for fasta in fasta_list:
        fasta.draw(context)
    
    ## Key
    draw_key(context)

    ## Saving file
    surface.write_to_png(f"{filename}.png")

def draw_key(context):
    for i, (motif, color) in enumerate(color_dict.items()):
        context.set_source_rgb(0,0,0)
        context.set_font_size(20)
        context.move_to(100, 25 * i + len(fasta_list) * 200 + 100)
        context.show_text(motif)

        context.set_source_rgb(color[0],color[1],color[2])
        context.set_line_width(10)
        context.move_to(20, 25 * i + len(fasta_list) * 200 + 100)
        context.line_to(80, 25 * i + len(fasta_list) * 200 + 100)
        context.stroke()

if __name__ == "__main__":
    args = get_args() 
    fasta = args.f
    motif_file = args.m
    file_prefix = fasta.split(".")[0]
    motif_dict = generate_motif_dict(motif_file)
    color_dict = generate_colors(motif_dict)
    fasta_list = parse_fasta(fasta)
    final_drawing(fasta_list,file_prefix)

