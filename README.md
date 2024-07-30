# Puppeteer Test Wrapper

## Description
This project provides a set of tools and scripts to automate testing using Puppeteer
in a remote environment. It utilizes DigitalOcean droplets for running the tests
and includes features for managing droplets,
uploading necessary files, and handling reports.

## Requirements

* Python v3.10 and above
* Poetry v1.8.2 and above
* DigitalOcean API key

## Installation

Place your DigitalOcean API key in a file at the path 
`~/.do/access_token`

### Installing the package manager poetry

* Instruction: [Python Poetry Installation Guide](https://python-poetry.org/docs/#installation)

To install the dependencies via poetry, run the command
`poetry install`

To activate the virtual environment, run the command
`poetry shell`

## Configuration Setup

Configuration files are located in the directory `configs`

### droplet_config.json - to configure the parameters of the DigitalOcean Droplet

Parameters:

`DROPLET_NAME` - (Required) The name assigned to the DigitalOcean droplet. 
Example: `"puppeteer-test"`

`DROPLET_REGION` - (Required) The region where the DigitalOcean droplet will be created.
Example: `"nyc3"` (New York 3)

`DROPLET_IMAGE` - (Required) The image (operating system) to be used for the DigitalOcean droplet.
Example: `"ubuntu-24-04-x64"` (Ubuntu 24.04, 64-bit)

`DROPLET_SIZE` - (Required) The size specification for the DigitalOcean droplet,
which determines its resources such as CPU and RAM.
Example: `"s-1vcpu-1gb"` (1 vCPU, 1 GB RAM)

`DEFAULT_USER` - (Required) The default user account to be used for accessing the droplet.
Example: `"root"`

`SSH_DO_USER_NAME` - (Optional) The name of the SSH key user configured on DigitalOcean.
If no name is specified, all existing keys on DigitalOcean will be added to the droplet.

`DO_PROJECT_NAME` - (Optional)The name of the project in DigitalOcean where the droplet will be moved to.


### puppeteer_chrome_config.json - Configuration file required to run puppeteer tests

Read more about the parameters [Puppeter Configuration Setup](https://github.com/ONLYOFFICE/Dep.Tests/tree/master/puppeteer#configuration-setup)

## Running Tests

To run tests execute the following command:

```bash
invoke run-test
```

This command has the following flags:

```bash
--save_droplet # - The droplet will not be deleted after the test run.
--retries [n] # - number of retries for running the test example
--threads [n] # - number of threads allocated for running the tests
--url_param [str] # - url parameters passed to the tester via the console
--params [n] # - values ​​transmitted to the tester
--out_directory [str] # - creates an output directory in the working folder
--prcache [boolean] # - preloading the cache for browsers
```
