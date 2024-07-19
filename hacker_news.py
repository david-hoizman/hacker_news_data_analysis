import requests
import csv
import matplotlib.pyplot as plt
from datetime import datetime


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
            'type': story_data.get('type')  # Adding type of the story (e.g., story, job, poll)
        }
        
        # Adding story date (UNIX timestamp)
        if 'time' in story_data:
            story_details['date'] = story_data['time']
        
        stories.append(story_details)
    
    return stories


def fetch_top_comments(top_stories):
    comments = []
    for story in top_stories:
        story_id = story['id']  # Using 'id' key instead of assuming 'id' is stored elsewhere
        
        story_comments_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story_comments_response = requests.get(story_comments_url)
        story_comments_data = story_comments_response.json()
        
        if story_comments_data is None:
            continue  # Skip to the next story if there's no response data
        
        if 'kids' in story_comments_data:  # 'kids' contains IDs of comments
            for comment_id in story_comments_data['kids']:
                comment_url = f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json'
                comment_response = requests.get(comment_url)
                comment_data = comment_response.json()
                
                if comment_data is None:
                    continue  # Skip to the next comment if there's no response data
                
                comment_details = {
                    'author': comment_data.get('by', 'Unknown'),  # Default to 'Unknown' if 'by' is missing
                    'text': comment_data.get('text', ''),
                    'time': comment_data.get('time', ''),
                    'parent_story_id': story_id
                }
                comments.append(comment_details)
    
    return comments


top_stories = fetch_top_stories()

top_comments = fetch_top_comments(top_stories)

# Saving top stories to CSV with additional fields
with open('top_stories.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'title', 'url', 'score', 'author', 'time', 'num_comments', 'type', 'date']  # Updated fieldnames
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for story in top_stories:
        writer.writerow(story)

# Saving top comments to CSV
with open('top_comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['author', 'text', 'time', 'parent_story_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for comment in top_comments:
        writer.writerow(comment)

# Function to analyze data
def analyze_data(top_stories):
    total_score = sum(story['score'] for story in top_stories)
    average_score = total_score / len(top_stories) if top_stories else 0
    
    total_comments = sum(story.get('num_comments', 0) for story in top_stories)
    num_stories_with_comments = sum(1 for story in top_stories if 'num_comments' in story and isinstance(story['num_comments'], int))
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

# Creating plots
labels = ['Average Score', 'Average Comments']
values = [statistics['average_score'], statistics['average_comments']]

plt.figure(figsize=(10, 5))

plt.bar(labels, values, color=['blue', 'green'])
plt.xlabel('Metrics')
plt.ylabel('Values')
plt.title('Average Score and Comments for Top Stories')

plt.savefig('metrics_plot.png')
plt.show()

# Plotting comments distribution over time
comment_times = [datetime.fromtimestamp(int(comment['time'])).strftime('%Y-%m-%d %H:%M:%S') for comment in top_comments if 'time' in comment]
hours = [int(time.split()[1].split(':')[0]) for time in comment_times if 'time' in comment]

plt.figure(figsize=(12, 6))
plt.hist(hours, bins=24, alpha=0.7, color='skyblue', edgecolor='black')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Comments')
plt.title('Distribution of Comments by Hour of the Day')
plt.xticks(range(24))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('comments_by_hour.png')
plt.show()

print("Data collection, analysis, and visualization completed successfully.")





































































































































