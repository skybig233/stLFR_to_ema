####
# name:stLFR_EMA
# author:jiangzhesheng
# date:2020.07.30
# function:Aligning stLFR reads to ref.fa using EMA
#	input:fastq1,fastq2,fasta
#	process:1.change stLFRdata to EMA data
#		2.EMA processing
#	output:1.step2_result directory(changedata result):interleaved data,whitelist,log
#	       2.step3_result directory(ema processing result):tmp files in ema processing(.fcnt/ncnt,preproc..)
#						alignment result file:ema_final.sam,ema_final.bam,*.log
####

#getopts print help function define
help()
{
    echo "This is stLRF_EMA"
    echo "!!!!!!please input ABSOLUTE path of fastq and fasta!!!!!!"
    echo "please input the parameters in command line like this:"
    echo "sh stLFR_EMA.sh -1 /dellfsqd2/ST_OCEAN/USER/jiangzhesheng/ema/ema_small/ema_small_data/chr19_reads1.clean.fastq.smcpy -2 /dellfsqd2/ST_OCEAN/USER/jiangzhesheng/ema/ema_small/ema_small_data/chr19_reads2.clean.fastq.smcpy -r /dellfsqd2/ST_OCEAN/USER/jiangzhesheng/rfa_data/chr19.fa -o result"
    echo "sh stLRF_EMA.sh "
    echo "here is parameters"
    echo " -1 ABSOLUTE path of INPUT_FASTQ1 "
    echo " -2 ABSOLUTE path of INPUT_FASTQ2"
    echo " -r ABSOLUTE path of INPUT_FASTA"
    echo " -o OUTPUT_DIR"
    echo " -h display this help"
}

echo ''EMA start : `date`''

####
#input parameters

if [ $# == 0 ]; then
	help
	exit 1
fi

while getopts ":1:2:r:o:h" opt;
do
	case $opt in
	1)	
		INPUT_FASTQ1="${OPTARG}"
		if [ ! -f "$INPUT_FASTQ1" ] ; then
		echo "$INPUT_FASTQ1 is not exist"
		exit 1
		fi
		;;
	2)
		INPUT_FASTQ2="${OPTARG}"
		if [ ! -f "$INPUT_FASTQ2" ] ; then
		echo "$INPUT_FASTQ2 is not exist"
		exit 1
		fi
		;;
	r)
		REF_FASTA="${OPTARG}"
		if [ ! -f "$REF_FASTA" ] ; then
		echo "$REF_FASTA is not exist"
		exit 1
		fi
		;;
	o)
		OUTPUT_DIR="${OPTARG}"
		;;
	h)	
		help
		exit 1
		;;
	\?)
		echo "wrong parameters"
		help
		exit 1
		;;
	esac
done
####
#processing

#step1.change_path
#ABSOLUTE path of OUTPUT_DIR is get
mkdir -p $OUTPUT_DIR

BASE_PATH=$(cd `dirname $0`;pwd)
CUR_PATH=$(pwd)
OUTPUT_DIR=$CUR_PATH/$OUTPUT_DIR

#step2.change stLFRdata to EMA data
##we will use stLFR_to_ema.py to convert stLFR data into EMA data
##and the EMA data is the interleaved.fastq file in step2_result
STEP2_OUTDIR_NAME="step2_result"
STEP2_OUTDIR=$OUTPUT_DIR/$STEP2_OUTDIR_NAME
echo "create folder:$STEP2_OUTDIR"
mkdir -p $STEP2_OUTDIR
/usr/bin/time -v \
python $BASE_PATH/stLFR_to_ema.py -1 $INPUT_FASTQ1 -2 $INPUT_FASTQ2 -o $STEP2_OUTDIR \
2>&1 | tee $STEP2_OUTDIR/result.log
echo ''stLFR_to_EMA step2 finished: `date`''


#step3.EMA processing
##we need the EMA data and whitelist as inputs which we get in step2
##result of EMA alignment file is ema_final.sam in step3_ema_result
##some tmp files is produced by EMA is in this directory,too
##log directory is the log files of each step and time.log is the summary log files 
INTERLEAVED_FASTQ=$OUTPUT_DIR/$STEP2_OUTDIR_NAME/interleaved.fastq
WHITELIST=$OUTPUT_DIR/$STEP2_OUTDIR_NAME/mywhitelist.txt
OUTDIR=$OUTPUT_DIR/step3_ema_result
LOGDIR="log"

mkdir -p $OUTDIR
cd $OUTDIR
mkdir -p $LOGDIR

echo "EMA processing"

#step3.1.EMA_count
##this step will create *.fcnt and *.ncnt file
/usr/bin/time -v \
parallel -j20 --bar "cat $INTERLEAVED_FASTQ | ema count -w $WHITELIST -o chr19 2>chr19.log" ::: {} \
2>&1 | tee $LOGDIR/count_time.log && tail -23 $LOGDIR/count_time.log 1>>time.log

#step3.2.EMA_preproc
##this step will create ema_preproc file and create 'ema-000-bin' like files
cat $INTERLEAVED_FASTQ | /usr/bin/time -v ema preproc -w $WHITELIST -n 500 -t 20 -o ema_preproc chr19.ema-ncnt \
2>&1 | tee $LOGDIR/preproc.log && tail -23 $LOGDIR/preproc.log 1>>time.log

#step3.3.EMA_align
##this step will align binning files in ema_preproc and create 'ema-000-bin.bam' like files for each bin
/usr/bin/time -v \
parallel --bar -j10 "ema align -t 2 -d -r $REF_FASTA -s {} | samtools sort  -@ 4 -O bam -l 0 -m 4G -o {}.bam -" ::: ./ema_preproc/ema-bin-??? \
2>&1 | tee $LOGDIR/align_time.log && tail -23 $LOGDIR/align_time.log 1>>time.log

#step3.4.EMA_nobc
##this step will align no barcode reads in ema-nobc and create ema-nobc.bam
/usr/bin/time -v \
bwa mem -p -t 20 -M -R "@RG\tID:rg1\tSM:sample1" $REF_FASTA ema_preproc/ema-nobc | samtools sort -@ 4 -O bam -l 0 -m 4G -o ema_preproc/ema-nobc.bam \
2>&1 | tee $LOGDIR/bwa.log && tail -23 $LOGDIR/bwa.log 1>>time.log

#step3.5.sambamba
##this step will add all bam files together and create ema_final.bam as a result
ulimit -n 4096
/usr/bin/time -v \
sambamba markdup -t 20 -p -l 0 ./ema_preproc/ema-nobc.bam ./ema_preproc/ema-nobc-dupsmarked.bam 
2>&1 | tee $LOGDIR/sambamba_nobc.log && tail -23 $LOGDIR/sambamba_nobc.log 1>>time.log

rm ./ema_preproc/ema-nobc.bam 

/usr/bin/time -v \
sambamba merge -t 20 -p ema_final.bam ema_preproc/*.bam \
2>&1 | tee $LOGDIR/sambamba_final.log && tail -23 $LOGDIR/sambamba_final.log 1>>time.log

echo ''EMA finished: `date`''

