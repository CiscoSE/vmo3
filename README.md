# VMO<sup>3

## Business/Technical Challenge
Have you ever set up your out of office message in Outlook, but forgot to enable your voice mail or change the greeting? 
Maybe you've returned to the office and forgot to disable that voice mail telling everyone that you are away.

VMO<sup>3</sup> allows users to enable their out of office message once and have it reflected across multiple platforms. 

## Proposed Solution

Our application will integrate O365 Exchange Out of Office alerting with Cisco Unity Connect (UCXN) and 
Cisco Unified Communication Manager (CUCM). Users can set their OoO alert in email and have it automatically enabled in 
voice mail. They will also receive an Webex Teams message that contains the number of the inbound caller and a separate 
Webex Teams message that contains the transcription of the message the caller leaves. 

<img src= "https://github.com/clintmann/vmo3/blob/master/images/vmo3_concept_image.gif" width="800" height="500" />


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

VMO<sup>3</sup> is made up of three microservices. Below is an architectural diagram of the components. The diagram also 
shows, at a high level, what each module interacts with. 

Both outlook-monitor and vmo-mediator were written in Python and uc-connector was written in PHP. 

This solution uses:
 - The Microsoft Graph development platform
 - An Office 365 mailbox
 - Cisco Unity Connection
 - Cisco Unified Communications Manager
 - Cisco Webex Teams
 - Amazon Polly for text to speech translation
 
 <img src= "https://github.com/clintmann/vmo3/blob/master/images/vmo3_architecture.gif" width="800" height="500" />


<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of the components involved with this project. e.g Python /  -->


## Usage

<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of how to use the solution  -->



## Installation

Since there are three distinct modules required, the detailed information for installation is included in the 
documentation links provided in the next section.


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
