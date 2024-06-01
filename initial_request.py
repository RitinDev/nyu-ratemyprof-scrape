import requests
import re

def make_initial_request(school_number):
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
        print(f"Result Count: {result_count}")
    else:
        print("No result count found.")
    
    if school_name_match:
        school_name = school_name_match.group(1)
        print(f"School Name: {school_name}")
    else:
        print("No school name found.")
    
    return {
        "school_id": school_id,
        "result_count": result_count,
        "school_name": school_name
    }

# Test the function
data = make_initial_request("675")