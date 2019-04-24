# VMO<sup>3

## Business/Technical Challenge
Have you ever set up your out of office message in Outlook, but forgot to change voice mail? 
Or maybe you've returned to the office and forgot to disable that voice mail telling everyone that you are away.

VMO<sup>3</sup> allows users to enable their out of office message once and have it reflected across multiple platforms. 

## Proposed Solution

Our application will integrate O365 Exchange Out of Office alerting with Cisco Unity Connect (UCXN) and 
Cisco Unified Communication Manager (CUCM). Users can set their OoO alert in email and have it automatically enabled in 
voice mail. They will also receive a daily listing of inbound calls, so they can see who called while they were 
out of the office, even if the person did not leave a voice mail. 

![LOGIC Workflow][logo]

[logo]: https://github.com/clintmann/vmo3/blob/master/images/vmo3_concept_image.gif "Workflow"


### Cisco Products Technologies/ Services

Our solution will leverage the following Cisco technologies

* [Cisco Unity Connection (UCXN)](https://www.cisco.com/c/en/us/products/unified-communications/unity-connection/index.html)
* [Cisco Unified Communications Manager (CUCM)](https://www.cisco.com/c/en/us/products/unified-communications/unified-communications-manager-callmanager/index.html)
* [Cisco WebEx Teams](https://www.webex.com/products/teams/index.html)

## Team Members

* Chris Bogdon <cbogdon@cisco.com> - Trans PNC
* Marty Sloan <masloan@cisco.com> - Midwest Atlantic Enterprise
* Clint Mann <climann2@cisco.com> - PA Liberty Select


## Solution Components


<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of the components involved with this project. e.g Python /  -->


## Usage

<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of how to use the solution  -->



## Installation

Since there are three distinct modules required, the detailed information for installation is included in the documentation links provided in the next section.


## Documentation

More detailed information and documentation can be provided in the following links:

* [outlook-monitor](outlook-monitor/README.md)
* [vmo-mediator](vmo-mediator/README.md)
* [uc-connector](https://github.com/sloan58/vmo3-uc/blob/master/README.md)


## License

Provided under Cisco Sample Code License, for details see [LICENSE](./LICENSE.md)

## Code of Conduct

Our code of conduct is available [here](./CODE_OF_CONDUCT.md)

## Contributing

See our contributing guidelines [here](./CONTRIBUTING.md)
