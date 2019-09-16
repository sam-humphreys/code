# CODE

## About

This repository serves as an example of my personal coding skills, just for fun. The codebase is wrote Python (3.6), however also hosts a touch of other technologies such as Docker, Kubernetes and Terraform.

**Feel free to browse or clone this repo!**

*Please note that some code may not work due to need for other resources. For example code which utilises Kubernetes will at minimum require a Kubernetes cluster and local authentication when using command line tools.*

---

## Setup

### Prerequisites
- Clone this repository (HTTPS) - `git clone https://github.com/sam-humphreys/code.git`
- Downloaded and installed Python (3.6 distribution) from [here](https://www.python.org/downloads/)

### Virtual Environment
Please ensure you completed all the prerequisites before continuing

1. Navigate into the cloned repository - `cd ~/code`
2. Install the Python library virtualenv - `pip3 install virtualenv`
3. Create a virtual environment - `virtualenv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install code as a Python library - `python setup.py install`
6. Install all other Python libraries - `pip install -r requirements.txt`
7. Update your Python path - `export PYTHONPATH=':/code'`

**SUCCESS!**

---

## Running Commands (CLI)

This project space uses [Click](https://click.palletsprojects.com/en/7.x/) to execute commands.

To run commands simply type `coderun` into the command line, followed by the `coderun [OPTIONS] COMMAND [ARGS]..` syntax. Typing `coderun` by itself will list all the available commands. To run an IPython interactive shell for example, enter - `coderun ipython`

To register a new command:
1. Write your functions by either creating a new `@click.group()` or adding to an existing group `@group.command()`
2. Write your new function nested under the group using `@group.command()`
3. If the group is not already listed/registered in the code workspace [main file](./code/main.py):

    a) Import the file you wrote your commands in

    b) Register it using the `main.add_command(code.folder.group)` syntax

---

## Continuous Integration (CI)

This repository uses [Docker Hub](https://hub.docker.com/) to handle CI. This works fine due to the low volume of code being pushed and it is also open-source (perfect for this purpose). Docker Hub has a Slack integration, so alerts on build/test status' can be tracked fairly easily. These alerts have direct links to the UI where full logs can be found for debugging or other requirements.

The way Docker Hub is configured, it will:
- Execute an intensive pytest run for each open pull request
- Each time a pull request is merged into master branch:
    - Automatically build the image
    - Due to the [docker compose test file](./docker-compose.test.yml), it will execute an intensive pytest run at the end of the build
    - Due to the Docker post push [file](./hooks/post_push), create a tag within the Docker Hub repository using the merged Git hash. This enables exact commit referencing, which can be seen in the image in this deployment [here](./gitops/k8s/deployments/watch-pods.yaml).

If the tests fail, the build will too fail, thus enabling smooth CI. This repository uses [Pytest](https://docs.pytest.org/en/latest/) and [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) to run a series of informed and property based tests.

To execute tests from the command line:
- All tests normally: `pytest`
- Change different hypothesis profiles:
    - Fast (less examples, shorter time limits): `pytest --hypothesis-profile=fast`
    - Intensive (more examples, longer time limits): `pytest --hypothesis-profile=intensive`
---