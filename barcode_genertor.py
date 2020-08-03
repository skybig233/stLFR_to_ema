import trans
import os
d={'0':'A','1':'T','2':'C','3':'G'}
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def barcodeGenertor(i,outputdir):
    if(i>=4**16):#
        logger.error("barcode is used up")
        return ''
    i=trans.tenToAny(4,i)
    i='0'*(16-len(i))+i
    ans=''
    for char in i:
        ans+=d[char]
    with open(os.path.join(outputdir,'mywhitelist.txt'), mode='a') as whitelist:
        whitelist.write(ans+'\n')
    return ans

