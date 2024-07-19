# Amazon Orders Scraper

## Overview

This project aims to develop an automatic agent that scrapes Amazon orders, retrieving their details in a structured format. The initial focus is on Amazon Egypt due to the availability of existing orders for testing.

## Approach

The project will be completed in two stages:

### Stage One: Manual Approach
In this stage, we will manually navigate the Amazon website using Selenium. This will help us understand the meta-steps required for the agent to function correctly and provide familiarity with Selenium.

### Stage Two: Automated Agent
In this stage, we will create a prompt to enable the model to use Selenium for interacting with the Amazon webpage. The agent will navigate to the order page and continue until all orders are downloaded.

## Plan

1. **Define a Prompt for the LLM**: Develop a prompt that allows the language model to generate accurate Selenium code.
2. **Error Handling**: Implement a function to retry operations if mistakes occur, enabling the agent to correct itself.
3. **Data Extraction**: 
    - Test the agent's ability to navigate all orders independently.
    - Evaluate the agent's capacity to extract structured information from the data.
        - Option 1: Extract relevant objects and use Python code for reliable data extraction.
        - Option 2: Use the LLM's capabilities to extract the information directly.

## Getting Started

### Prerequisites

- Python 3.x
- Selenium
- WebDriver for your preferred browser (e.g., ChromeDriver)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/bely66/amazon-orders-scraper.git
    cd amazon-orders-scraper
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```


### Usage

#### Stage One: Manual Approach

1. Run the manual scraping script to understand the process:
    ```bash
    python login_amazon.py
    ```

2. Follow the instructions to navigate and extract order details manually.

#### Stage Two: Automated Agent

1. Update the prompt and agent configuration as needed in `agent_config.py`.

2. Run the automated agent script:
    ```bash
    python login_amazon_smart.py
    ```

3. Monitor the agent's progress and review the extracted data.

### Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.
