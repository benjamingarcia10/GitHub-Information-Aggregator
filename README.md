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
