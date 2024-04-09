import json
from apiclient import get_access_token;

def replace_token(position):
    with open('appsconfig.json', 'r') as reddit_keys_file:
        app = json.loads(reddit_keys_file.read())['apps'][position]
        token = get_access_token(app['client_id'], app['client_secret'], app['user_agent'])
        
        with open('tokens.txt', 'r') as token_file_read:
            lines = token_file_read.read().splitlines()
            lines[position] = token

        with open('tokens.txt', 'w') as token_file_write:
            token_file_write.write('\n'.join(lines))


def main():
    with open('appsconfig.json', 'r') as reddit_keys_file:
        keys = json.loads(reddit_keys_file.read())['apps']
        
        tokens = [get_access_token(app['client_id'], app['client_secret'], app['user_agent']) for app in keys]
        
        with open('tokens.txt', 'w') as token_file:
            token_file.write('\n'.join(tokens))
        
if __name__ == "__main__":
    main()