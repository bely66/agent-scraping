# Amazon Orders Scraper

## Overview

This project aims to develop an automatic agent that scrapes Amazon orders, retrieving their details in a structured format. The initial focus is on Amazon Egypt due to the availability of existing orders for testing.

## Strategy to Develop an Automated Data Scraping Agent for Amazon

#### Strategy Overview:
1. **Initial Manual Process**:
   - Perform the entire data scraping process manually to understand each step thoroughly.
   - This includes reading library documentation, understanding and debugging code errors, reading HTML contents of the pages, and interacting with page elements.

2. **Incremental Automation**:
   - Abstract and automate each step identified in the manual process.
   - Ensure the agent can handle various challenges, such as slow internet speeds and handling ads or popups.

3. **Quality and Adaptability**:
   - Develop the agent with qualities such as robust abstraction of manual steps and adaptability to handle unexpected scenarios.
   - Envision a "super agent" that can complete tasks with minimal input, such as "scrape Amazon orders using the following username and password."

#### Phased Implementation Plan:

##### Phase 1: Basic Functionality
- **Agent 1**: Generates Selenium code to fetch product details based on detailed instructions.
- **Agent 2**: Extracts data using Beautiful Soup code, also based on detailed instructions.

##### Phase 2: Enhanced Automation with Feedback
- **Agent 1**: Executes Selenium code multiple times, incorporating feedback from the website to improve performance.
- **Agent 2**: Explores HTML patterns to generate more efficient Beautiful Soup code.

##### Phase 3: Generalized Instructions
- **Agent 1** and **Agent 2**: Operate based on more general instructions, reducing the need for detailed guidance.

##### Phase 4: Unified Intelligent Agent
- Combine the functionalities of the two agents into a single, highly autonomous agent that can perform the entire scraping process with minimal input.


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
