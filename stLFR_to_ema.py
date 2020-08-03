import barcode_genertor
import os
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('-1','--inputfastq1')
parser.add_argument('-2','--inputfastq2')
parser.add_argument('-o','--outputdir')
args=parser.parse_args()

try:
    inputfastq1=args.inputfastq1
    inputfastq2=args.inputfastq2
    outputdir=args.outputdir
except Exception as e:
    print('woops')
#
# inputfastq1 = "C:\\Users\DELL\Desktop\chr19_reads1.clean.fastq.smcpy"
# inputfastq2 = "C:\\Users\DELL\Desktop\chr19_reads2.clean.fastq.smcpy"
# outputdir = os.getcwd()

i = 0


def readAndChange(file, last_id, last_barcode):
    global i
    ID = file.readline()
    base = file.readline()
    cflag = file.readline()
    quality = file.readline()
    ID_list = ID.strip().split('\t')
    well_ID = ID_list[0][ID_list[0].index('#') + 1:-2]
    ID = ID_list[0]

    if (last_id == well_ID):
        barcode = last_barcode
    else:
        i = i + 1
        barcode = barcode_genertor.barcodeGenertor(i,outputdir)

    if (ID[-1] == '1'):
        ID = ID[:-2] + ' 1:N:0:0\n'
        ans = ID + barcode + 'T' * 7 + base + cflag + 'S' * 23 + quality
    else:
        ID = ID[:-2] + ' 3:N:0:0\n'
        ans = ID + base + cflag + quality

    # ans = ID + barcode + '(16base)' + 'TTTTTTT(7base)' + base + cflag + quality  # debug
    # ans = ID + barcode + 'T'*7 + base + cflag + 'S'*23 + quality
    return ans, well_ID, barcode


well_id_list = []
last_id = ''
last_barcode = ''
with open(inputfastq1, mode='r') as fq1, open(inputfastq2, mode='r') as fq2, open(os.path.join(outputdir,'interleaved.fastq'), mode='w') as outfq:
    while (True):
        try:
            ans, last_id, last_barcode = readAndChange(fq1, last_id, last_barcode)
            outfq.write(ans)
            ans, last_id, last_barcode = readAndChange(fq2, last_id, last_barcode)
            outfq.write(ans)
        except Exception:
            break
