import praw
import config
import time
import os
import re
from lxml import html
from bs4 import BeautifulSoup
import requests

# go to https://www.reddit.com/prefs/apps to create an app
# called once when the bot begins running
def bot_login():
    reddit = praw.Reddit(username = config.username,
                        password = config.password,
                        client_id = config.client_id,
                        client_secret = config.client_secret,
                        user_agent = "humblebundle game lister v0.1") 
                        # if your bot gets abused, reddit will ban your user_agent
                        # simply change your user_agent to gain access to reddit again 
                        # most user_agents will have a version number which can be incremented in case of a ban
    return reddit

def run_bot(reddit):
    subreddit = reddit.subreddit(config.subreddit)
    print('Scanning posts')

    for submission in subreddit.new(limit=25):
        if (submission.author != reddit.user.me() 
        and submission.id not in submissions_replied_to 
        and term.search(submission.title) 
        and url_term.search(submission.url) 
        and not url_exclude.search(submission.url)):

            print('\n------------------------------------------------------------------------\n')
            print(submission.title,'\n')

            humble_page = requests.get(submission.url)
            humble_soup = BeautifulSoup(humble_page.content, 'html.parser')
            is_game_bundle = humble_soup.find('a', class_='tabbar-tab-is-active-dark', href='/', text=re.compile('game bundles', re.IGNORECASE))
            if not is_game_bundle:
                print('Not a game bundle')
                continue

            # each game_row corresponds to one of the payment tiers
            game_rows = humble_soup.find_all('div', class_='dd-game-row')
            tier_list = []
            for row in game_rows:
                tier = {}
                tier_name = row.find('h2', class_='dd-header-headline')
                tier['tier_name'] = tier_name.get_text().strip()
                tier['titles'] = []
                tier['urls'] = []
                tier['platforms'] = []
                tier['tcards'] = []

                game_titles = row.find_all('div', class_='dd-image-box-caption')
                game_images = row.find_all('div', class_='dd-image-box')

                # gets and strips raw text for game titles
                for game_title in game_titles:
                    title = game_title.get_text().strip()
                    tier['titles'].append(title)

                # checks for Steam support icon for each game on HumbleBundle page
                for image in game_images:
                    platform_img = image.find('i', class_='hb-steam')
                    platform = 'Steam' if platform_img else 'Other'
                    tier['platforms'].append(platform)

                # if on Steam, gets Steam store url and Trading Card support
                # if not on Steam, gets Google url instead
                for i in range(0, len(tier['platforms'])):
                    platform = tier['platforms'][i]
                    title = tier['titles'][i]
                    if platform == 'Steam':
                        steam_search = requests.get('http://store.steampowered.com/search/suggest?term='+title+'&f=games&cc=US&lang=english&v=2286217')
                        tree = html.fromstring(steam_search.content)
                        url = tree.xpath('//a/@href')[0]
                        url_split = re.split('\?snr', url)
                        url = url_split[0]
                        tier['urls'].append(url)
                        steam_page = requests.get(url)
                        steam_soup = BeautifulSoup(steam_page.content, 'html.parser')
                        tcard_link = steam_soup.find('a', text='Steam Trading Cards')
                        tier['tcards'].append('Yes' if tcard_link else 'No')
                    else:
                        tier['urls'].append('https://www.google.com/#q='+title)
                        tier['tcards'].append('N/A')
            
                # Cleans up tier name and sets short name
                if re.search('what you want', tier['tier_name'], re.IGNORECASE):
                    tier['tier_name'] = 'Pay What You Want'
                    tier['short_name'] = 'PWYW'
                elif re.search('average', tier['tier_name'], re.IGNORECASE):
                    tier['tier_name'] = 'Beat The Average'
                    tier['short_name'] = 'BTA'
                else:
                    tier_name_split = re.split('(Pay \$\d* or more)', tier['tier_name'], re.IGNORECASE)
                    tier['tier_name'] = tier_name_split[1]
                    tier['short_name'] = re.split('(\$\d*)', tier['tier_name'])[1]

                tier_list.append(tier)

            # creates the comment
            comment = ''
            comment += 'Tier|Game|Platform|Trading Cards?\n:--:|:--:|:--:|:--:|:--:\n'
            for i in range(0, len(tier_list)):
                for j in range(0, len(tier_list[i]['titles'])):
                    short_name = tier_list[i]['short_name']
                    title = tier_list[i]['titles'][j]
                    url = tier_list[i]['urls'][j]
                    platform = tier_list[i]['platforms'][j]
                    tcards = tier_list[i]['tcards'][j]
                    comment += ''+short_name+'|['+title+']'+'('+url+')|'+platform+'|'+tcards+'\n'

            comment += config.footer
            print(comment)

            submission.reply(comment)

            # keeps list of submissions already replied to in a .txt
            submissions_replied_to.append(submission.id)
            with open('submissions_replied_to.txt', 'a') as f:
                f.write(submission.id + '\n')

    # use this if you have no other means of automation
    # print('Sleeping for 5')
    # time.sleep(5)

# restores submissions already replied to
def get_saved_submissions():
    if not os.path.isfile('submissions_replied_to.txt'):
        submissions_replied_to = []
        return submissions_replied_to

    with open('submissions_replied_to.txt', 'r') as f:
        submissions_replied_to = f.read().split('\n')
        submissions_replied_to = list(filter(None, submissions_replied_to))

    return submissions_replied_to

reddit = bot_login()
term = re.compile('^\[humble\s?bundle].*bundle', re.IGNORECASE)
url_term = re.compile('https://www.humblebundle.com')
url_exclude = re.compile('https://www.humblebundle.com/store')
submissions_replied_to = get_saved_submissions()
print(submissions_replied_to)
run_bot(reddit)