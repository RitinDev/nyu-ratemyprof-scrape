import pandas as pd
import requests
import re

# School number on ratemyprofessors.com
school_number = "5724"

"""
Make a simple get request to the URL to get the following variables:

- schoolID: The ID of the school
- resultCount: The total number of professors to scrape data for
- schoolName: The name of the school as displayed on ratemyprofessors.com

Returns a tuple of (schoolID, resultCount, schoolName)
"""


def make_initial_request(school_number: int) -> tuple:
    url = f"https://www.ratemyprofessors.com/search/professors/{school_number}?q=*"

    # Make a get request to the URL and store the response as string
    response = requests.get(url).text

    # From the response, parse the schoolID and responseCount

    # Regular expression pattern to match the schoolID
    school_id_pattern = r'"schoolID\\":\\"(.*?)\\",'

    # Regular expression pattern to match the resultCount
    result_count_pattern = r'"resultCount":(\d+),'

    # Regular expression pattern to match the school name
    school_name_pattern = r'"__typename":"School","name":"(.*?)"'

    # Search for the patterns in the string
    school_id_match = re.search(school_id_pattern, response)
    result_count_match = re.search(result_count_pattern, response)
    school_name_match = re.search(school_name_pattern, response)

    if school_id_match:
        school_id = school_id_match.group(1)
        print(f"School ID: {school_id}")
    else:
        print("No school ID found.")

    if result_count_match:
        result_count = result_count_match.group(1)
        result_count = int(result_count)
        print(f"Result Count: {result_count}")
    else:
        print("No result count found.")

    if school_name_match:
        school_name = school_name_match.group(1)
        print(f"School Name: {school_name}")
    else:
        print("No school name found.")

    return (school_id, result_count, school_name)


"""
Get the data for each Professor.

Makes a post request to the graphql endpoint, which returns data for chunk_size professors at a time.
We have to scrape the data in chunks to avoid hitting the rate limit and causing an error.
A cursor is used to keep track of where we are in the response.

Returns a list of dictionaries containing the data
"""


def get_teacher_data(
    school_number: str, school_id: str, result_count: int, chunk_size=1000
):
    url = "https://www.ratemyprofessors.com/graphql"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Basic dGVzdDp0ZXN0",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": "ccpa-notice-viewed-02=true",
        "Origin": "https://www.ratemyprofessors.com",
        "Referer": f"https://www.ratemyprofessors.com/search/professors/{school_number}?q=*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
    }

    all_results = []
    has_next_page = True
    cursor = ""

    while has_next_page and len(all_results) < result_count:
        body = {
            "query": """
            query TeacherSearchPaginationQuery(
              $count: Int!
              $cursor: String
              $query: TeacherSearchQuery!
            ) {
              search: newSearch {
                ...TeacherSearchPagination_search_1jWD3d
              }
            }

            fragment TeacherSearchPagination_search_1jWD3d on newSearch {
              teachers(query: $query, first: $count, after: $cursor) {
                didFallback
                edges {
                  node {
                    ...TeacherCard_teacher
                    id
                    __typename
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
                resultCount
                filters {
                  field
                  options {
                    value
                    id
                  }
                }
              }
            }

            fragment TeacherCard_teacher on Teacher {
              id
              legacyId
              avgRating
              numRatings
              ...CardFeedback_teacher
              ...CardSchool_teacher
              ...CardName_teacher
              ...TeacherBookmark_teacher
            }

            fragment CardFeedback_teacher on Teacher {
              wouldTakeAgainPercent
              avgDifficulty
            }

            fragment CardSchool_teacher on Teacher {
              department
              school {
                name
                id
              }
            }

            fragment CardName_teacher on Teacher {
              firstName
              lastName
            }

            fragment TeacherBookmark_teacher on Teacher {
              id
              isSaved
            }
            """,
            "variables": {
                "count": min(chunk_size, result_count - len(all_results)),
                "cursor": cursor,
                "query": {
                    "text": "",
                    "schoolID": f"{school_id}",
                    "fallback": True,
                    "departmentID": None,
                },
            },
        }

        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        if (
            "data" in data
            and "search" in data["data"]
            and "teachers" in data["data"]["search"]
        ):
            teachers_data = data["data"]["search"]["teachers"]
            if teachers_data["edges"]:
                all_results.extend([edge["node"] for edge in teachers_data["edges"]])
                has_next_page = teachers_data["pageInfo"]["hasNextPage"]
                cursor = teachers_data["pageInfo"]["endCursor"]
            else:
                has_next_page = False
        else:
            has_next_page = False
            print("Error in response:", data)

        # Print status to monitor progress
        print(f"Fetched {len(all_results)} teachers so far...")

    return all_results[:result_count]


data = make_initial_request(school_number)
school_id, result_count, school_name = data

# Make another request with the result count
data = get_teacher_data(school_number, school_id, result_count)

# Extract the required variables and create a DataFrame
parsed_data = []

for entry in data:
    full_name = f"{entry['firstName']} {entry['lastName']}"
    rating = entry["avgRating"]
    department = entry["department"]
    difficulty = entry["avgDifficulty"]
    num_ratings = entry["numRatings"]

    parsed_data.append(
        {
            "Name": full_name,
            "Average Rating": rating,
            "Department": department,
            "Difficulty Rating": difficulty,
            "Number of Ratings": num_ratings,
        }
    )

# Convert scraped Professor data to DataFrame
df = pd.DataFrame(parsed_data)
# Keep only unique rows
df = df.drop_duplicates()
# Remove rows with Number of Ratings of 0
df = df[df["Number of Ratings"] != 0]

# Make the school's name filename friendly
school_filename = school_name.replace(" ", "-").lower()

# Save the df as a json file
df.to_json(f"{school_filename}-prof-data.json", orient="records")
