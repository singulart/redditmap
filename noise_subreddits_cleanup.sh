# Input file containing the values to be replaced
FILE="noise_subreddits.txt"

# Loop through each line in the file
while IFS= read -r line
do
    echo $line
    sed -i -- "s/\[\[${line}\]\]//g" obsidian-map/*.md
done < "$FILE"

echo "Cleanup complete."
