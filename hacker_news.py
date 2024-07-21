import requests
import csv
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
from constants import *


def fetch_top_stories():
    """
    Retrieves details of the top stories from Hacker News API.

    Returns:
        list: A list of dictionaries, each containing details of a top story.
    """
    
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    response = requests.get(url)
    
    top_story_ids = response.json()
    stories = []
    
    for story_id in top_story_ids[:NUM_OF_TOP_STORIES]:  # Fetching details of the top x stories
        
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
    """
    Retrieves comments related to each top story.

    Args:
        top_stories (list): List of dictionaries representing top stories.

    Returns:
        list: A list of dictionaries, each containing details of a top comment.
    """
    
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

def write_to_csv(file_name, fieldnames, data):
    """
    Writes data to a CSV file.

    Args:
        file_name (str): The name of the CSV file to write.
        fieldnames (list): List of field names (headers) for the CSV file.
        data (list of dict): List of dictionaries representing rows of data.
    """
    
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

def analyze_data(top_stories):
    """
    Analyzes data related to top stories.

    Args:
        top_stories (list): List of dictionaries representing top stories.

    Returns:
        dict: A dictionary containing calculated statistics (average score and average comments).
    """
     
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
    
# def create_plot(top_comments, statistics):
#     """
#     Creates a bar plot for average score and average comments.

#     Args:
#         top_comments (list): List of dictionaries representing top comments.
#         statistics (dict): Dictionary containing calculated statistics.
#     """    
       
#     labels = ['Average Score', 'Average Comments']
#     values = [statistics['average_score'], statistics['average_comments']]

#     plt.figure(figsize=(10, 5))

#     plt.bar(labels, values, color=['blue', 'green'])
#     plt.xlabel('Metrics')
#     plt.ylabel('Values')
#     plt.title('Average Score and Comments for Top Stories')

#     plt.savefig('metrics_plot.png')
#     plt.show()

#     comment_times = [datetime.fromtimestamp(int(comment['time'])).strftime('%Y-%m-%d %H:%M:%S') for comment in top_comments if 'time' in comment]
#     hours = [int(time.split()[1].split(':')[0]) for time in comment_times]

#     plt.figure(figsize=(12, 6))
#     plt.hist(hours, bins=24, alpha=0.7, color='skyblue', edgecolor='black')
#     plt.xlabel('Hour of the Day')
#     plt.ylabel('Number of Comments')
#     plt.title('Distribution of Comments by Hour of the Day')
#     plt.xticks(range(24))
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
#     plt.tight_layout()
#     plt.savefig('comments_by_hour.png')
#     plt.show()

def create_plot(top_comments, statistics):
    """
    Creates plots for average score and average comments, and comments distribution by hour.

    Args:
        top_comments (list): List of dictionaries representing top comments.
        statistics (dict): Dictionary containing calculated statistics.
    """    
    
    # Plot for average score and average comments
    labels = ['Average Score', 'Average Comments']
    values = [statistics['average_score'], statistics['average_comments']]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color=['blue', 'green'])
    plt.xlabel('Metrics')
    plt.ylabel('Values')
    plt.title('Average Score and Comments for Top Stories')
    plt.savefig('metrics_plot.png')
    plt.close()

    # Plot for comments distribution by hour
    comment_hours = [datetime.fromtimestamp(int(comment['time'])).hour for comment in top_comments if 'time' in comment]
    hour_counts = Counter(comment_hours)
    
    hours = range(24)
    counts = [hour_counts.get(hour, 0) for hour in hours]

    plt.figure(figsize=(12, 6))
    plt.bar(hours, counts, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Comments')
    plt.title('Distribution of Comments by Hour of the Day')
    plt.xticks(range(0, 24, 2))  # Show every other hour for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('comments_by_hour.png')
    plt.close()

def create_statistics(top_stories):
    """
    Calculates statistics (average score and average comments) and saves them to a CSV file.

    Args:
        top_stories (list): List of dictionaries representing top stories.

    Returns:
        dict: Dictionary containing calculated statistics.
    """
    
    # Analyzing the collected data
    statistics = analyze_data(top_stories)

    # Saving statistics to a CSV file
    with open('statistics.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['metric', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'metric': 'average_score', 'value': statistics['average_score']})
        writer.writerow({'metric': 'average_comments', 'value': statistics['average_comments']})

    return statistics

if __name__ == "__main__":
    
    # Fetch data
    try: 
        top_stories = fetch_top_stories()
        top_comments = fetch_top_comments(top_stories)
    except:
        raise Exception ("Sorry, the fetch was failed")

    # Saving top stories to CSV with additional fields
    write_to_csv('top_stories.csv', ['id', 'title', 'url', 'score', 'author', 'time', 'num_comments', 'type', 'date'], top_stories)

    # Saving top comments to CSV with additional fields
    write_to_csv('top_comments.csv', ['author', 'text', 'time', 'parent_story_id'],top_comments)

    # Calculates statistics and saves in a CSV file
    statistics = create_statistics(top_stories)

    # Creating plots
    create_plot(top_comments, statistics)
    
    print("Data collection, analysis, and visualization completed successfully.")
