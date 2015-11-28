# This gets BAM and their corresponding BAI files and retrieves data before deleting both downloaded files.
# Priyank Purohit, November 19, 2015

# This regex matches to the link paths in the txt file.
match_regex='/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits.bam'
for i in $(cat data/iplant_path_to_rnaseq_bam_files.txt); do # Iterate over the paths in the txt file
	BAM_PATH="$(echo $i | grep -v 'bai$' | grep -P $match_regex)" # ignore the BAI file paths, match the regex above
	if [[ $BAM_PATH == *".bam"* ]] # If the match contains the .bam extension, proceed:
	then
		echo ''
		echo ''
		echo ''
		echo ''
		echo '>>> START <<<'
		BAM_LINK='http://s3.amazonaws.com/iplant-cdn'$BAM_PATH #add the correct prefix
		BAI_LINK='http://s3.amazonaws.com/iplant-cdn'$BAM_PATH'.bai' #add the correct prefix and .bai suffix
		FILE_NAME=$(basename "$BAM_LINK" ".bam") # The name of the target bam file
		FILE_NAME=$FILE_NAME'.bam' # Add the extension because the above cmd removes the extension...
		
		out_file_name=${BAM_LINK:66} # generate unique BAM file name
		out_file_name=${out_file_name////_} #replace the / with _

		# Download the BAM and its BAI file
		echo '>>> '$BAM_LINK
		wget -P mpileups/temp/ $BAM_LINK
		echo '>>> '$BAI_LINK
		wget -P mpileups/temp/ $BAI_LINK

		# Get the mpileup
		echo '>>> GETTING MPILEUPS'
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr1:3631-5899 > mpileups/$out_file_name

		# Delete the downloaded BAM and BAI files
		echo '>>> DELETING BOTH FILES.'
		rm mpileups/temp/$FILE_NAME &
		rm mpileups/temp/$FILE_NAME'.bai' &
		echo '>>> END <<<'
	fi
done