import requests
import slack
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import collections
import time
from dateutil import parser


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
    created:>2022-11-01", type: ISSUE, first: 100) {
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
            timelineItems(itemTypes: REVIEW_REQUESTED_EVENT, first: 10) {
              nodes {
                ... on ReviewRequestedEvent {
                  createdAt
                  
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
  }
"""
result = run_query(query) # Execute the query

user_pending_pr_count_map = dict(
    collections.Counter(
        [review_requests['requestedReviewer']['login']
        for edge in result['data']['search']['edges'] 
        for review_requests in edge['node']['timelineItems']['nodes']]
    )
)



print_payload = "Counts of reviews pending on PRs created since Nov 1 2022" + "\n"
for dev in user_pending_pr_count_map:
    print_payload+=dev + " : " + str(user_pending_pr_count_map[dev])+"\n"

print_payload+="\n"+"Review requests pending for more than a day"

for edge in result['data']['search']['edges']:
    for reviewnode in edge['node']['timelineItems']['nodes']:
        if ts - float(parser.parse(reviewnode['createdAt']).strftime('%s')) > 86400:
            print_payload+="\n"+reviewnode['requestedReviewer']['login']+" : "+edge['node']['url']
print(print_payload)
client.chat_postMessage(channel='#sandbox',text=print_payload)
