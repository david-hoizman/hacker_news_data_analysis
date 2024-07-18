import requests
import csv
import matplotlib.pyplot as plt


def fetch_top_stories():
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    response = requests.get(url)
    top_story_ids = response.json()
    
    stories = []
    for story_id in top_story_ids[:10]:  # Fetching details of the top 10 stories
        story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story_response = requests.get(story_url)
        story_data = story_response.json()
        
        story_details = {
            'id': story_id,
            'title': story_data.get('title'),
            'url': story_data.get('url'),
            'score': story_data.get('score'),
            'author': story_data.get('by'),
            'time': story_data.get('time'),
            'num_comments': story_data.get('descendants'),
            'type': story_data.get('type'),  # Adding type of the story (e.g., story, job, poll)
            'date': story_data.get('time')  # Adding date of the story
        }
        stories.append(story_details)
    
    return stories

def fetch_top_comments(top_stories):
    comments = []
    for story in top_stories:
        story_id = story['id']  # Using 'id' key instead of assuming 'id' is stored elsewhere
        
        story_comments_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story_comments_response = requests.get(story_comments_url)
        story_comments_data = story_comments_response.json()
        
        if 'kids' in story_comments_data:  # 'kids' contains IDs of comments
            for comment_id in story_comments_data['kids']:
                comment_url = f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json'
                comment_response = requests.get(comment_url)
                comment_data = comment_response.json()
                
                comment_details = {
                    'author': comment_data.get('by'),
                    'text': comment_data.get('text'),
                    'time': comment_data.get('time'),
                    'parent_story_id': story_id
                }
                comments.append(comment_details)
    
    return comments


top_stories = fetch_top_stories()

top_comments = fetch_top_comments(top_stories)

# Saving top stories to CSV with additional fields
with open('top_stories.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'title', 'url', 'score', 'author', 'time', 'num_comments', 'type', 'max_comments', 'date']  # Updated fieldnames
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for story in top_stories:
        writer.writerow({
            'id': story['id'],
            'title': story['title'],
            'url': story['url'],
            'score': story['score'],
            'author': story['author'],
            'time': story['time'],
            'num_comments': story['num_comments'],
            'type': story['type'],
            'max_comments': 100,  # Placeholder for maximum comments, replace with actual data if available
            'date': story['date']  # Adding date field
        })

# Saving top comments to CSV
with open('top_comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['author', 'text', 'time', 'parent_story_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for comment in top_comments:
        writer.writerow(comment)

def analyze_data(top_stories):
    total_score = sum(story['score'] for story in top_stories)
    average_score = total_score / len(top_stories) if top_stories else 0
    
    total_comments = 0
    num_stories_with_comments = 0
    
    for story in top_stories:
        if 'num_comments' in story and isinstance(story['num_comments'], int):
            total_comments += story['num_comments']
            num_stories_with_comments += 1
    
    average_comments = total_comments / num_stories_with_comments if num_stories_with_comments > 0 else 0
    
    statistics = {
        'average_score': average_score,
        'average_comments': average_comments
    }
    
    return statistics



# Analyzing the collected data
statistics = analyze_data(top_stories)

# Saving statistics to a CSV file
with open('statistics.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['metric', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'metric': 'average_score', 'value': statistics['average_score']})
    writer.writerow({'metric': 'average_comments', 'value': statistics['average_comments']})

