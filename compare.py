import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-q','--querysam')
parser.add_argument('-r','--referencesam')
parser.add_argument('-p','--prefix',default='')
args=parser.parse_args()

try:
    querysam=args.querysam
    referencesam=args.referencesam
    prefix=args.prefix
except Exception as e:
    print('woops')

def flagTheRead(ID,flag):
    if(flag%128>=64):
        ID=ID+'/1'
    if (flag % 256 >= 128):
        ID=ID+'/2'
    return ID

def getPosition(string):#input a SA\XA string output a position list
    tmp=[]
    stringlist=string.split(';')

    for i in stringlist:
        try:
            if(i!='\n'):
                tmp.append(int(i.split(',')[1]))
        except IndexError:
            return tmp
            # print(string+"\n"+'i:'+i)
    return tmp
def getSAXA(fieldlist):
    SA=[]
    XA=[]
    for i in fieldlist:
        if ('SA' in i):
            SA=getPosition(i)
        if('XA' in i):
            XA=getPosition(i)
    return SA,XA

# referencesam="C:\\Users\\DELL\\Desktop\\ema_final.sam.smcpy"
# querysam="C:\\Users\\DELL\\Desktop\\bwa-mem-aln-pe.sam.smcpy"
# prefix=''

d={}
match=0
unmatch=0
nokey=0
distance_1_10=0
distance_11_100=0
match_to_SA=0
match_to_XA=0
small_data_n=100

unmatchlist=prefix+'_unmatchlist'
nokeylist=prefix+'_nokeylist'
count=prefix+'_count'

with open(querysam,mode='r') as querysamfile,\
        open(referencesam,mode='r') as referencesamfile,\
        open(unmatchlist,mode='w')as unmatchlistfile,\
        open(nokeylist,mode='w')as nokeylistfile, \
        open(count, mode='w')as countfile:
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
                SA_positionlist,XA_positionlist=getSAXA(line_list[11:])
                if(int(d[queryID]) in SA_positionlist):
                    match_to_SA+=1
                if(int(d[queryID]) in XA_positionlist):
                    match_to_XA+=1
                distance = int(queryposition) - int(d[queryID])
                absolute_distance=abs(distance)
                if(absolute_distance<=10):
                    distance_1_10+=1
                elif(absolute_distance<=100):
                    distance_11_100+=1

                if(unmatch<small_data_n):
                    unmatchlistfile.write("distance="+str(distance)+"\n")
                    unmatchlistfile.write(line)
        except KeyError:
            nokey+=1
            if(nokey<small_data_n):
                nokeylistfile.write(line)

    match="match:"+str(match)+'\n'
    unmatch="unmatch:"+str(unmatch)+'\n'
    distance_1_10="distance_1_10:"+str(distance_1_10)+'\n'
    distance_11_100="distance_11_100:" + str(distance_11_100)+'\n'
    nokey="nokey:"+str(nokey)+'\n'
    match_to_SA="match_to_SA:"+str(match_to_SA)+'\n'
    match_to_XA="match_to_XA:"+str(match_to_XA)+'\n'

    log=match+unmatch+match_to_SA+match_to_XA+distance_1_10+distance_11_100+nokey
    countfile.write(log)
    print(log)
    # print("match:"+str(match))
    # print("unmatch:"+str(unmatch))
    # print("distance_1_10:"+str(distance_1_10))
    # print("distance_11_100:"+str(distance_11_100))
    # print("nokey:"+str(nokey))