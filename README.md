# Commuto Protocol
#TODO: Update readme <br>
The Commuto Protocol is a decentralized exchange that allows users to exchange fiat currencies and stablecoins quickly, 
affordably, safely, and in a censorship-resistant manner, without the use of a trusted intermediary.

For more information, please consult the whitepaper draft, which can be found here:
https://github.com/jimmyneutront/commuto-whitepaper

## About this Repository

This repository contains only the core Commuto Protocol smart contract code, as well as unit and integration testing 
code for the core protocol. The Commuto Protocol is intended to be used with either a graphical, text-based/command line
or API interface, to allow easy interaction with the core protocol functionality. These interfaces will make up a 
peer-to-peer network across which offers will be broadcast, so each user will have a complete local copy of the Commuto 
Protocol's decentralized offer book. However, this project is in the very early stages of development and work on the 
interfaces has not yet begun.

Currently, there is no community forum or chat room for Commuto. Please feel free to open an issue in this repository or
the whitepaper's repository with any questions, suggestions, feature requests, or bugs. You can contact the developer 
via Matrix or Keybase using the information in his bio.

## Testing/Developing the Commuto Protocol

The reccomended IDE for Commuto Protocol development is PyCharm CE with the Intellij Solidity plugin installed.

Set up a Commuto Protocol development and testing environment with the following steps:

1. Clone the git repository:

   ```
   $ git clone https://github.com/jimmyneutront/commuto-protocol.git
   ```

2. Enter the new directory:

   ```
   $ cd commuto-protocol
   ```
   
3. Ensure that you have Python 3.7 or later installed:

   ```
   $ python3 --version
   ```
   
4. Create a new virtual environment in the project directory:

   ```
   $ python3 -m venv .venv
   ```
   
5. Use pip to install the following packages: `web3`, `slither-analyzer`, `solc-select` and `py-solc-x`:

   ```
   $ pip install web3 slither-analyzer solc-select py-solc-x
   ```

6. Use solc-select to install solc 0.6.12:

   ```
   $ solc-select install 0.6.12
   ```
   
7. Set 0.6.12 as the global version of solc:

   ```
   $ solc-select use 0.6.12
   ```
   
8. Download and install [Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

9. Create and enter new directory and initialize a new npm project: 

   ```
   $ mkdir commuto-test-chain
   $ cd commuto-test-chain
   $ npm init
   ```

10. Install [Hardhat](https://hardhat.org):

   ```
   $ npm install --save-dev hardhat
   ```
   
11. Start a standalone Hardhat Network instance:

   ```
   $ npx hardhat node
   ```
   
12. Replace the web3 provider address in [CommutoSwapTest.py](https://github.com/jimmyneutront/commuto-protocol/blob/f29c18e0757c4f79ce9335b8ec863d7de762ffb8/tests/CommutoSwapTest.py#L10) and [Setup_Test_Environment.py](https://github.com/jimmyneutront/commuto-protocol/blob/f29c18e0757c4f79ce9335b8ec863d7de762ffb8/Setup_Test_Environment.py#L14) with the address and port number of your Hardhat Network instance.

13. You are now ready to run tests and experiment with the Commuto Protocol!

   ```
   $ cd ../tests
   $ python3 -m unittest
   ```

Before submitting any pull requests, run Commuto_Swap_Tests.py and Commuto_Swap_Integration_Tests.py, and run
Slither on the project as well. Do not submit a pull request if Commuto_Swap_Tests or Commuto_Swap_Integration_Tests do 
not pass. Attempt to resolve all issues raised by Slither. However, if an issue cannot be resolved for any reason, 
include a comment with the code in question to explain why.