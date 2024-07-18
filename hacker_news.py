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
        
        # Calculate number of top-level comments (kids)
        max_comments = len(story_data.get('kids', []))
        
        story_details = {
            'id': story_id,
            'title': story_data.get('title'),
            'url': story_data.get('url'),
            'score': story_data.get('score'),
            'author': story_data.get('by'),
            'time': story_data.get('time'),
            'num_comments': story_data.get('descendants'),
            'max_comments': max_comments
        }
        stories.append(story_details)
    
    return stories


def analyze_data(top_stories):
    total_score = sum(story['score'] for story in top_stories)
    average_score = total_score / len(top_stories) if top_stories else 0
    
    total_comments = 0
    num_stories_with_comments = 0
    max_comments = 0
    
    for story in top_stories:
        if 'num_comments' in story and isinstance(story['num_comments'], int):
            total_comments += story['num_comments']
            num_stories_with_comments += 1
        
        if story['max_comments'] > max_comments:
            max_comments = story['max_comments']
    
    average_comments = total_comments / num_stories_with_comments if num_stories_with_comments > 0 else 0
    
    statistics = {
        'average_score': average_score,
        'average_comments': average_comments,
        'max_comments': max_comments
    }
    
    return statistics


top_stories = fetch_top_stories()

with open('top_stories.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'title', 'url', 'score', 'author', 'time', 'num_comments', 'max_comments']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for story in top_stories:
        writer.writerow(story)

statistics = analyze_data(top_stories)

with open('statistics.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['metric', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'metric': 'average_score', 'value': statistics['average_score']})
    writer.writerow({'metric': 'average_comments', 'value': statistics['average_comments']})
    writer.writerow({'metric': 'max_comments', 'value': statistics['max_comments']})

























































