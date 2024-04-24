import os
import re
import subprocess

# Any subreddit that is interacted with by less than 'link_weight_to_remove' Redditors will be removed from the map
# This script was useful when I used Obsidian to visuaize interactions, but may not be useful otherwise
link_weight_to_remove = 100 

def grep_search(directory, pattern: str):
    # Prepare the grep command. Use -l to only output filenames and -E for extended regex
    pattern = pattern.replace('[', '\\[').replace(']', '\\]')
    cmd = ['grep', '-lR', pattern, directory]
    
    # Run the grep command and capture output
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Split the output by newlines to get a list of matching files
    matching_files = result.stdout.split('\n')
    
    # Remove empty strings from the list
    matching_files = [file for file in matching_files if file]
    
    return matching_files


def remove_subreddit(file, pattern: str):
    cmd = ['sed', '-i', '', f"s/{pattern}//g", file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Split the output by newlines to get a list of matching files
    if result.stderr: 
        print(result.stderr)

def remove_irrelevant_subreddits(directory, match):
    matching_files = grep_search(directory, match)
        
    # If there's exactly one matching file, remove the reference to this sub from the file
    if len(matching_files) <= link_weight_to_remove:
        for f in set(matching_files):
            remove_subreddit(f, match.replace('[', '\\[').replace(']', '\\]'))
            print(f"Deleted subreddit in {matching_files[0]}")

def process_files(directory, regex_pattern):
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        # Make sure it's a file
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Find all regex matches in the file content
            matches = re.findall(regex_pattern, content)
            # print(set(matches))
            
            for match in set(matches):
                remove_irrelevant_subreddits(directory, match)

# Example usage
directory = '../cleanup-experiment'
regex_pattern = r'([\[]{2}\w*[\]]{2})'
process_files(directory, regex_pattern)
