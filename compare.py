import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-q','--querysam')
parser.add_argument('-r','--referencesam')
args=parser.parse_args()

try:
    querysam=args.querysam
    referencesam=args.referencesam
except Exception as e:
    print('woops')

def flagTheRead(ID,flag):
    if(flag%128>=64):
        ID=ID+'/1'
    if (flag % 256 >= 128):
        ID=ID+'/2'
    return ID

# referencesam="C:\\Users\\DELL\\Desktop\\bwa-mem-aln-pe.sam.smcpy"
# querysam="C:\\Users\\DELL\\Desktop\\ema_final.sam.smcpy"

d={}
match=0
unmatch=0
nokey=0
distance_1_10=0
distance_11_100=0

unmatchlist='unmatchlist'
nokeylist='nokeylist'
with open(querysam,mode='r') as querysamfile,\
        open(referencesam,mode='r') as referencesamfile,\
        open(unmatchlist,mode='w')as unmatchlistfile,\
        open(nokeylist,mode='w')as nokeylistfile:
    #1.create refer dic
    for line in referencesamfile:
        line_list=line.split('\t')
        line_list[0]=flagTheRead(line_list[0],int(line_list[1]))
        if(line_list[0] in d):
            print('error')
        else:d[line_list[0]]=line_list[3]
    #2.find query
    for line in querysamfile:
        line_list=line.split('\t')
        line_list[0]=flagTheRead(line_list[0],int(line_list[1]))
        queryID=line_list[0]
        queryposition=line_list[3]
        try:
            if(d[queryID]==queryposition):
                match+=1
            else:
                unmatch+=1
                distance = int(queryposition) - int(d[queryID])

                if(distance<=10):
                    distance_1_10+=1
                elif(distance<=100):
                    distance_11_100+=1

                if(unmatch<100):
                    unmatchlistfile.write("distance="+str(distance)+"\n")
                    unmatchlistfile.write(line)
        except KeyError:
            nokey+=1
            if(nokey<100):
                nokeylistfile.write(line)
    print("match:"+str(match))
    print("unmatch:"+str(unmatch))
    print("distance_1_10:"+str(distance_1_10))
    print("distance_11_100:"+str(distance_11_100))
    print("nokey:"+str(nokey))