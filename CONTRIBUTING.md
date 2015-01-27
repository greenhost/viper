# How to contribute to Viper

Patches from the community are more than welcome to make sure Viper is working properly. We want to make it as easy as possible for others to contribute.

## Building from source

### Windows
To build Viper on windows you will need the following software installed on a mahcine running Windows 7 or later.

#### To build the reference client
* .NET SDK 4.0 or greater
* Visual Studio 2010 Express or greater

#### To build the Windows service
* ActivePython 2.7.8.10 (Python 2.7)

Once ActivePython is installed you must install the python modules that Viper depends on, these modules are listed in the requirements.txt file. And you can install them via pip like this:

````pip install -r third-party\requirements.txt````

#### To build the installer
* NSIS 2.46 (makensis must be in your path for the build-script to work)

Once your build machine has this software readily available you should be able to run the build.bat script and build a binary of the service.

## Ways to contribute

### Report any bugs you find
* Make sure you have a [GitHub account](https://github.com/signup/free)
* If you think you found a bug, submit a ticket via Github.
  * Clearly describe the issue including steps to reproduce it is a bug.
  * Note the earliest version that you know has the issue.

### Request a feature you would like to see implemented
Use the github issues to tell us what you would like to see implemented. Tell us why you need the feature you are asking for.

### Build your own GUI client
If you have some mad UX skills you might want to develop a better user-facing UI. Most of the networking code in Viper is taken care of by the Windows service that runs in the background. The GUI client just interacts with the service using a simple JSON/REST API. Using this API you can control the basic functions of Viper.

Have a look at the [API specification here](doc/daemon-api.yaml). You can use the [Swagger editor](http://editor.swagger.io) to render a pretty document from the YAML spec source.

### Rolling up your sleeves and making your own changes
* Fork the repository on GitHub
* Create a topic branch from where you want to base your work.
  * This is usually the master branch.
  * To quickly create a topic branch based on master; `git branch
    fix/master/my_contribution master` then checkout the new branch with `git
    checkout fix/master/my_contribution`.  Please avoid working directly on the
    `master` branch.
* It helps if each commit you make has a clear and very specific purpose.
* Check for unnecessary whitespace with `git diff --check` before committing.
* Make sure your commit messages are in the proper format.

* Make sure you have added any necessary tests for your changes. Typically
  only refactoring and documentation changes require no new tests.
* Run _all_ the tests to assure nothing else was accidentally broken.

## Submitting Changes
* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository in the [greenhost](https://github.com/greenhost) organization.

