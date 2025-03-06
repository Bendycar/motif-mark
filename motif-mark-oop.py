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

IUPAC_codes = {'A':'[Aa]', 'C': '[Cc]','G':'[Gg]','T':'[Tt]','U':'[Tt]', 'R':'[AGag]','Y':'[CTct]','S':'[GCgc]','W':'[ATat]','K':'[GTgt]','M':'[ACac]','B':'[CGTcgt]','D':'[AGTagt]','H':'[ACTact]','V':'[ACGacg]','N':'[ACTGactg]',
               'a':'[Aa]', 'c': '[Cc]','g':'[Gg]','t':'[Tt]','u':'[Tt]', 'r':'[AGag]','y':'[CTct]','s':'[GCgc]','w':'[ATat]','k':'[GTgt]','m':'[ACac]','b':'[CGTcgt]','d':'[AGTagt]','h':'[ACTact]','v':'[ACGacg]','n':'[ACTGactg]'
               }

class Motif:
    def __init__(self, seq, start, stop, order):
        self.start = start
        self.stop = stop
        self.seq = seq
        self.order = order
        self.color = color_dict[seq]
        self.red, self.green, self.blue = self.color 
    
    def draw_motif(self, context):
        context.set_source_rgb(self.red, self.green, self.blue)
        context.set_line_width(40)
        context.move_to(self.start + 100, 200 * self.order)
        context.line_to(self.stop + 100, 200 * self.order)
        context.stroke()

        

class FastaRecord:
    def __init__(self, gene, order, seq, RC: bool):
        self.gene = gene
        self.seq = seq
        self.RC = RC
        self.order = order
        self.start, self.end = self.find_exon(seq)
        self.motif_list = self.find_motifs(seq, motif_dict)
        self.length = len(seq)
    
    def __repr__(self):
        return f"Order: {self.order}"#"motifs: {self.motif_list}"#f"FASTA record with gene {self.gene} and sequence {self.seq} (Reverse complemented: {self.RC})"
    
    def find_motifs(self, seq, motif_dict):
        motifs = []
        for motif, regex in motif_dict.items():
            matches = re.finditer(regex, seq)
            for match in matches:
                motifs.append(Motif(motif, match.start() + 1, match.end(), self.order))
        return motifs

    def find_exon(self, seq):
        exon = re.search(r'[A-Z]+', seq)
        if exon:
            start = exon.start() # Returns 0-indexed start position of matching group
            end = exon.end()
        return (start + 1, end) # I want to use 1-based indexing
    
    def draw(self, context):
        context.set_source_rgb(0, 0, 0)
        context.set_line_width(2)
        context.move_to(100, 200 * self.order)  #(x,y)
        context.line_to(self.length + 100, 200 * self.order)
        context.stroke()

        context.set_source_rgb(0,0,0)
        context.set_line_width(30)
        context.move_to(self.start + 100, 200 * self.order)
        context.line_to(self.end + 100, 200 * self.order)
        context.stroke()
        
        context.set_source_rgba(0, 0, 0, 1)
        context.set_font_size(25) 
        context.move_to(50, 200 * self.order - 50)
        context.show_text(f"Gene: {self.gene}")

        for motif in self.motif_list:
            motif.draw_motif(context)


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
    return motifs
        
def generate_colors(motiflist) -> dict:
    colors_dict = {}
    options = range(0,256,32) # All generated values must be at least 32 away on at least one element of the RGB scale in order to appear distinct
    for motif in motiflist:
        red = random.choice(options) / 255
        green = random.choice(options) / 255
        blue = random.choice(options) / 255
        colors_dict[motif] = (red, green, blue)
    return colors_dict

def parse_fasta(fastapath: str) -> list:
    fasta_list = []
    seq = ""
    gene = None
    order = 0
    with open(fastapath, "r") as fh:
        for line in fh:
            if line.startswith('>'):
                if gene: #Should only not happen the first line, where gene will be None
                    order += 1
                    record = FastaRecord(gene,order,seq,RC)#After that, every time a header will be encountered the record will be written
                    fasta_list.append(record)
                gene = re.match(r">(\S+)", line).group(1) # Literal > followed by any number of non-whitespace characters
                rev_comp = "reverse complement" in line.lower() 
                RC = bool(rev_comp) #Establishing values for next record
                seq = "" #Initializing empty string for next record
            else:
                seq += line.strip() # Adding every non-header line to the sequence string
    order += 1 # Adding final record
    record = FastaRecord(gene,order,seq,RC)
    fasta_list.append(record)
    return fasta_list

def final_drawing(fasta_list, filename): 
    width = 1100 # Hard coded because we know no sequences are longer than 1000
    height = len(fasta_list) * 200 + len(motif_dict) * 70 # Account for number of genes and size of key
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    context = cairo.Context(surface)
    context.set_source_rgb(1, 1, 1)
    context.rectangle(0, 0, width, height) # White background
    context.fill()
    for fasta in fasta_list:
        fasta.draw(context)
    draw_key(context)
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

    # color = dict_of_motif_color[m]
    # context.set_source_rgb(color[0],color[1],color[2])  
    # context.set_line_width(10)
    # context.move_to(20, i*30 + (len(list_of_geneGroups)*100) + 145)  #(x,y)
    # context.line_to(80,i*30 + (len(list_of_geneGroups)*100) + 145)
    # context.stroke()


if __name__ == "__main__":

    args = get_args() 
    fasta = args.f
    motif_file = args.m
    file_prefix = fasta.split(".")[0]
    motif_dict = generate_motif_dict(motif_file)
    color_dict = generate_colors(motif_dict)
    fasta_list = parse_fasta(fasta)
    final_drawing(fasta_list,file_prefix)
    #key = generate_colors(motif_list)

