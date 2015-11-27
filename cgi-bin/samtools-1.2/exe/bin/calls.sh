# This regex matches to the link paths in the txt file.
match_regex='/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits.bam'
# Iterate over the paths in the txt file
for i in $(cat iplant_path_to_rnaseq_bam_files.txt); do
	# ignore the BAI file paths, match the regex above
	BAM_PATH="$(echo $i | grep -v 'bai$' | grep -P $match_regex)"
	if [[ $BAM_PATH == *".bam"* ]] # If the match contains the .bam extension, proceed:
	then
		BAM_LINK='http://s3.amazonaws.com/iplant-cdn'$BAM_PATH #add the correct prefix
		out_file_name=${BAM_LINK:66} # new unique BAM file name
		out_file_name=${out_file_name////_} #replace the / with _
		echo '>>> '$out_file_name
		./samtools mpileup -d 800000 -r Chr1:3631-5899 $BAM_LINK > mpileups/$out_file_name
	fi
done
./samtools