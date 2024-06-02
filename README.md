# RateMyProfessors Scraper

This Python notebook allows you to scrape data for all professors in a given school from RateMyProfessors. By inputting the school's number, the script collects data for the professors of that school by making calls to RateMyProfessors' GraphQL backend.

## Features

- Scrapes professor data from RateMyProfessors using GraphQL queries.
- Handles up to 1000 professors per request, with support for chunked data collection.
- Outputs data in a structured format for further analysis or use.

## Prerequisites

- Python 3.11 or higher
- Jupyter Notebook
- Required Python packages: pandas, requests, re

## Usage

1. Find your school's number on RateMyProfessors. For example, NYU has the number 675, as seen in the URL: `https://www.ratemyprofessors.com/school/675`.

2. Open the `prof-scrape.ipynb` notebook.

3. Replace the placeholder school number with your school's number in the appropriate cell of the notebook.

4. Run all cells in the notebook to start the data collection process, along with some preliminary analysis.

## Output

The script will output the collected data on a school's professors in a json format, which can further be converted to a pandas DataFrame.

## Limitations

- The script can only collect data for up to 1000 professors per request due to RateMyProfessor's GraphQL query limit. As such, if a school has more than 1000 professors, the script will collect data for the professor in chunks, which takes a little longer.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## Acknowledgments

- This project makes use of user submitted ratings from [RateMyProfessors](https://www.ratemyprofessors.com/).