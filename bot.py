import requests
import slack
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import collections
import time

ts = time.time()
print(ts)

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
  search(query: "org:Partsavatar-Team is:open is:pr sort:created-asc
  created:>2021-12-01", type: ISSUE, first: 100) {
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
          reviewRequests(first: 100) {
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
#print(issue_count)

user_pending_pr_count_map = dict(
    collections.Counter(
        [review_requests['requestedReviewer']['login']
        for edge in result['data']['search']['edges'] 
        for review_requests in edge['node']['reviewRequests']['nodes']]
    )
)
print(user_pending_pr_count_map)
print_payload = "Counts of reviews pending on PRs created since Dec 1 2021" + "\n"
for dev in user_pending_pr_count_map:
    print_payload+=dev + " : " + str(user_pending_pr_count_map[dev])+"\n"



client.chat_postMessage(channel='#general',text=print_payload)
