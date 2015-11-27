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
		echo '>>> GETTING MPILEUPS + READ MAPS'

		# AT1G01010
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr1:3631-5899 > mpileups/AT1G01010/$out_file_name
		echo -n $out_file_name >> mpileups/AT1G01010/read_counts_wc_method.txt
		samtools view mpileups/temp/$FILE_NAME Chr1:3631-5899 | wc -l >> mpileups/AT1G01010/read_counts_wc_method.txt
		
		# AT2G24270
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr2:10327050-10329941 > mpileups/AT2G24270/$out_file_name
		echo -n $out_file_name >> mpileups/AT2G24270/read_counts_wc_method.txt
		samtools view mpileups/temp/$FILE_NAME Chr1:3631-5899 | wc -l >> mpileups/AT2G24270/read_counts_wc_method.txt
		
		# AT3G24650
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr3:8997370-9001063 > mpileups/AT3G24650/$out_file_name
		echo -n $out_file_name >> mpileups/AT3G24650/read_counts_wc_method.txt
		samtools view mpileups/temp/$FILE_NAME Chr1:3631-5899 | wc -l >> mpileups/AT3G24650/read_counts_wc_method.txt
		
		# AT3G24660
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr3:9003576-9005943 > mpileups/AT3G24660/$out_file_name
		echo -n $out_file_name >> mpileups/AT3G24660/read_counts_wc_method.txt
		samtools view mpileups/temp/$FILE_NAME Chr1:3631-5899 | wc -l >> mpileups/AT3G24660/read_counts_wc_method.txt
		
		# AT5G66460
		samtools mpileup mpileups/temp/$FILE_NAME -d 8000 -r Chr5:26538395-26541036 > mpileups/AT5G66460/$out_file_name
		echo -n $out_file_name >> mpileups/AT5G66460/read_counts_wc_method.txt
		samtools view mpileups/temp/$FILE_NAME Chr1:3631-5899 | wc -l >> mpileups/AT5G66460/read_counts_wc_method.txt
		

		# Delete the downloaded BAM and BAI files
		echo '>>> DELETING BOTH FILES.'
		rm mpileups/temp/$FILE_NAME &
		rm mpileups/temp/$FILE_NAME'.bai' &
		echo '>>> END <<<'
	fi
done
