import os
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-i','--inputsam')
parser.add_argument('-o','--outputdir')
parser.add_argument('-t','--tag')
args=parser.parse_args()

try:
    inputsam=args.inputsam
    outputdir=args.outputdir
    tag=args.tag
except Exception as e:
    print('woops')

# inputsam = "C:\\Users\\DELL\\Desktop\\bwa-mem-aln-pe.sam.smcpy"
# outputdir = os.getcwd()
# tag='XA'

def tagInField(tag,field_list):
    for i in field_list:
        if(tag in i):
            return True
    return False

with open(inputsam,mode='r') as inputsamfile,open(os.path.join(outputdir,tag+'.sam'),mode='w')as tagfile, open(os.path.join(outputdir,'no'+tag+'.sam'),mode='w') as notagfile:
    for line in inputsamfile:
        field_list=line.split('\t')[11:]
        if tagInField(tag,field_list):
            tagfile.write(line)
        else:notagfile.write(line)