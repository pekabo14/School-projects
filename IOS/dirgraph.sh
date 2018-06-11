#!/usr/bin/env bash

# IOS - projekt 1
# AUTOR: Peter Kapicak
POSIXLY_CORRECT=yes
# Arguments options (getopts)
N_FLAG=false
while getopts ":i:n" opt;
do
	case $opt in
		i )  
			I_FLAG=true
			regex="$OPTARG"
			;;
		n )  
			N_FLAG=true
			;;
		\? )
			echo "Invalid option: -$OPTARG" >&2
			exit 1
			;;
		: )
			echo "Invalid option: -$OPTARG requires an argument" >&2
			exit 1
			;;
		esac
done
shift $((OPTIND -1))

# DIR is save to variable
path_arg="$1"
# check if variable is empty
# if true, then print current working directory
if [ -z "$path_arg" ]
	then
		echo "Root directory: ."
# check if path_arg is directory
	elif [ ! -d "$path_arg" ]
		then
			echo "Argument $path_arg is not directory" >&2
			exit 1
# if variable path_arg is not empty print DIR from argument
	else
		echo "Root directory: $path_arg"
		cd "$path_arg"
fi

# testing if it is in terminal
# if it is true return number of cols of terminal
# if not return 79 cols
if [ -t 1 ]
	then
		num_cols=$(tput cols)
		num_cols=$((num_cols-1))
	else
		num_cols=79
fi

# count number of directories
# variable count_dir is bigger than 0

# if -i arguments is set
if [ "$I_FLAG" = true ]
	then
		count_dir=$(find . -type d | sed 's/.\///' | awk -v regex="$regex" 'BEGIN{FS = "/"} {
			h_var=0
			for (count = 1; count <= NF; count++)
			{
				if ($count ~ regex) h_var=1
			}
			if (h_var != 1) print $0
			
		}' | wc -l)
	else
		count_dir=$(find . -type d | wc -l)
fi

if [ "$I_FLAG" = true ]
	then
		count_file=$(find . -type f | sed 's/.\///' | awk -v regex="$regex" 'BEGIN{FS = "/"} {
			h_var=0
			for (count = 1; count <= NF; count++)
			{
				if ($count ~ regex) h_var=1
			}
			if (h_var != 1) print $0
			
		}' | wc -l)
	else
		count_file=$(find . -type f | wc -l)
fi


echo "Directories: $count_dir"
echo "All files: $count_file"

#============================================================
#	FILE SIZE HISTOGRAM
#============================================================
# histogram for sizes of files
# find all files... 'du' give sizes in Bytes
if [ "$I_FLAG" = true ]
	then
		size_hist=$(find -type f | sed 's/.\///' | awk -v regex="$regex" 'BEGIN{FS = "/"} {
			h_var=0
			for (count = 1; count <= NF; count++)
			{
				if ($count ~ regex) h_var=1
			}
			if (h_var != 1) print $0
			
		}' | xargs du -b | awk '{print $1}')
	else
		size_hist=$(find . -type f -exec du -b {} + | awk '{print $1}')
fi

# counting how much files are in categories
size_f='size_f'
for size in $size_hist
do
	if [ "$size" -lt 100 ]; then # less than 100 B
		m=1
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 1024 ]; then # less than 1 KiB
		m=2
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 10240 ]; then # less than 10 KiB
		m=3
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 102400 ]; then # less than 100 KiB
		m=4
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 1048576 ]; then # less than 1 MiB
		m=5
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 10485760 ]; then # less than 10 MiB
		m=6
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 104857600 ]; then # less than 100 MiB
		m=7
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	elif [ "$size" -lt 1073741824 ]; then # less than 1 GiB
		m=8
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	else									# equal or greater than 1 GiB
		m=9
		eval ${size_f}${m}="'$((size_f${m}+1))'"
	fi 	
done
# find the category with the biggest number of files
size_max=0
		for i in $(seq 1 9)
		do
			int=$(echo $(eval echo \$$size_f${i}))
			if [ -z "$int" ]
				then
					int=0
			fi
			if [ "$int" -gt "$size_max" ]
				then
					size_max="$int"
			fi
			size_length=$(printf "%s\n%s" "$size_length" "$int")
		done
# if normalization is set...
if [ "$N_FLAG" = true ]
	then
		max_l=$((num_cols-12))
		res="$max_l"
		oldIFS="$IFS" # store IFS
		IFS=$'\n' # set new IFS
		if [ "$max_l" -lt "$size_max" ]
			then
				for i in $(echo "$size_length" | sed 1d)
				do
					if [ "$i" -ne "$size_max" ]
						then
							bet=$((i*max_l/size_max))
							res=$(printf "%s\n%s" "$res" "$bet")
					fi
				done
				size_length="$res"
		fi
fi
# store names of Categories 
size_counter=1 # variable for store ranges of size 
size_cnt='size_cnt'
for i in "<100 B" "<1 KiB" "<10 KiB" "<100 KiB" "<1 MiB" "<10 MiB" "<100 MiB" "<1 GiB" ">=1 GiB"
do
	eval ${size_cnt}${size_counter}="'${i}'" # store ranges
	size_counter=$((size_counter+1))
done
# printing FSHIST
echo "File size histogram:"
# change numbers for '#'
c=1
for i in $size_length
do # store one range for output
	size_fi=$(echo $(eval echo \$$size_cnt${c}))
	for ((j=1; j<=$i; j++)) 
	do
		cro+='#'
	done
	# print one line of histogram
	printf "  %-8s: %s\n" "$size_fi" "$cro" 
	cro=''
	c=$((c+1))
done
IFS="$oldIFS"

#===========================================================
#	FILE TYPE HISTOGRAM
#===========================================================

echo "File type histogram:"

# find all types of files in directory and cut type greater than 40 char.
if [ "$I_FLAG" = true ]
	then
		pole=$(find -type f | sed 's/.\///' | awk -v regex="$regex" 'BEGIN{FS = "/"} {
			h_var=0
			for (count = 1; count <= NF; count++)
			{
				if ($count ~ regex) h_var=1
			}
			if (h_var != 1) print $0
			
		}' | xargs file | awk '{$1="";$0=$0;$1=$1}1' | cut -c 1-40)
	else
		pole=$(find -type f -exec file {} + | awk '{$1="";$0=$0;$1=$1}1' | cut -c 1-40)
fi


# sort file types by the most occurence type, number of same types and store first 10
sep_pole=$(printf "%s" "$pole" | sort | uniq -c | sort -gr | head)

oldIFS="$IFS" # store IFS
IFS=$'\n' # set new IFS
# if normalization is set
if [ "$N_FLAG" = true ]
	then
		tss=$((num_cols-47))
		numero=$(echo $sep_pole | awk '{print $1}')
		tst=$(echo "$sep_pole" | head -1 | awk '{$1="";$0=$0;$1=$1}1')
		final=$(printf "%s %s" "$tss" "$tst")
		src=$(echo "$sep_pole" | sed 1d)
		if [ "$tss" -lt "$numero" ]
			then
				for i in $src
				do
					num=$(echo $i | awk '{print $1}')
					str=$(echo $i | awk '{$1="";$0=$0;$1=$1}1')
					add=$((num*tss))
					add=$((add/numero))
					final=$(printf "%s\n%s %s" "$final" "$add" "$str")
				done
				sep_pole="$final"
		fi
fi

# printing FTHIST
for i in $sep_pole
do
	file_name=$(echo $i | awk '{$1="";$0=$0;$1=$1}1')
	file_num=$(echo $i | awk '{print $1}')

	IFS="$oldIFS"
	for ((j=1; j<=$file_num; j++))
	do
		cross+='#'
	done
	
	if [ "${#file_name}" -ge 40 ]
		then
			printf "  %-40s...: %s\n" "$file_name" "$cross"
			cross=''
		else
			printf "  %-43s: %s\n" "$file_name" "$cross"
			cross=''
	fi
done

exit 0
