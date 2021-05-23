# GitHub Information Aggregator
### What?
* Aggregates basic GitHub user and public repository information
* JSON response endpoint
* Webpage with dynamically loaded information based on username
* Ability to use GitHub access token to increase rate limits
* Uses multithreading to allow for fast information retrieval

### Setup
1. Install [Python3](https://www.python.org/downloads/) and be sure to install pip and add Python to PATH as well using the Python installer.
2. Clone this repository or download files and extract all files to a folder.
3. Install all dependencies for this project
	- Open a CMD/Powershell window in the root directory of the project and run the following command:
		- ``pip3 install -r requirements.txt``
		- Ensure there are no errors when running the command.
4. (Optional) Configure .env file to increase GitHub rate limits or specify a different port (default is port 5000)
    - Refer [here](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) to view the GitHub documentation for help on creating a GitHub token.
    - The only required scope you need to select for the token is "public_repo" which allows the use of your token to access public repositories.
    - Create a ".env" file in the root directory of the project and paste these lines in replacing the text after "=" with your desired info (both fields are optional but the token is recommended to prevent unauthenticated rate limits):
      ```
      GITHUB_ACCESS_TOKEN=<YOUR GITHUB ACCESS TOKEN>
      PORT=<DESIRED PORT NUMBER>
      ```
5. Run the api.py file and the terminal should indicate the ip and port that the server is now running on.

## Usage
There are two ways to retrieve the GitHub aggregated information:
1. JSON API Endpoint
    - Utilize the API endpoint by typing the server location with an "/api" at the end and appending the requested username in a username query variable
    - (Optional) Append the "forked" query variable with "true" or "false" to indicate if you want to include forked repositories in the information or not (default is true)
    - Examples:
    ```
   http://127.0.0.1:5000/api?username=user
   http://127.0.0.1:5000/api?username=user&forked=false
    ```
2. Webpage
    - Visit the server location.
    - Example: ``http://127.0.0.1:5000``
    - Enter the username in the username text box and check/uncheck the checkbox indicating if you want to view forked repositories or not

## API Disclaimer
[View the GitHub rate limit documentation here](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)

Unauthenticated requests are limited to 60 requests per hour. Depending on how many repositories the username 
you are retrieving data for has, you may exceed the 60 requests per hour very quickly. If you exceed the limit, 
GitHub will rate limit the origin IP (IP of the server requesting information) and both paths will return indicating 
a GitHub API error. To bypass this, follow the steps indicated in #4 of the setup section above. This will increase 
your rate limit to 5,000 requests per hour.
