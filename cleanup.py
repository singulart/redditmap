import os
import re
import subprocess

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

def remove_subreddit_if_unique_match(directory, file, match):
    matching_files = grep_search(directory, match)
        
    # If there's exactly one matching file, remove the reference to this sub from the file
    if len(matching_files) == 1:
        remove_subreddit(matching_files[0], match.replace('[', '\\[').replace(']', '\\]'))
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
                remove_subreddit_if_unique_match(directory, file, match)

# Example usage
directory = './cleanup-experiment'
regex_pattern = r'([\[]{2}\w*[\]]{2})'
process_files(directory, regex_pattern)
