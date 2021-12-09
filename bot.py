import requests
import slack
import json
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
from glom import glom


env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
GITHUBTOKEN = os.environ['GITHUB_TOKEN']
TOKEN = "Bearer " + GITHUBTOKEN
headers = {"Authorization": TOKEN}


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

query = """
{
  search(query: "org:Partsavatar-Team is:open is:pr sort:created-asc created:>2021-12-01", type: ISSUE, first: 10) {
    issueCount
    edges {
      node {
        ... on PullRequest {
          number
          title
          repository {
            nameWithOwner
          }
          createdAt
          url
          reviewRequests(first: 10) {
            nodes {
              requestedReviewer {
                ... on User {
                  login
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
result = run_query(query) # Execute the query

issue_count = result['data']['search']['issueCount']
print(issue_count)
df_data = pd.json_normalize(result['data']['search']['edges'])
#filtered_df = df_data[['node.title','node.createdAt','node.url','node.nodes']['node.reviewRequests.nodes']]

filtered_df = df_data['node.reviewRequests.nodes']
#filtered_df['reviewer'] = df_data['node.reviewRequests.nodes'].apply(lambda row: glom(row, 'requestedReviewer.login'))
filtered_df['reviewer'] = df_data['node.reviewRequests.nodes']
#df = pd.DataFrame(df_data)
print(filtered_df)
print(df_data.columns)








client.chat_postMessage(channel='#general',text='Hello World')
