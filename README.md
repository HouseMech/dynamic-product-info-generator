# Dynamic Product Information Generator
The project takes a product name, searches for it and then returns product info in JSON, assisted by ChatGPT. It attempts to mitigate the hallucinations a typical LLM might experience by scraping data from E-commerce stores and then using GPT to identify the important information.

This was developed for a coding challenge for my application to Inceptiv Inc. It was an interesting challenge, although complicated by the open-ended nature of the challenge's requirements and the variety of pitfalls one could encounter.

# Setup
Ensure you have a `.env` file within the project diretory that contains an OpenAI key.
```
OPENAI_API_KEY=your_key_here
```
Afterwards run `fastapi run main.py` to start the project. Navigate to `http://0.0.0.0:8000/getProductInfo/` and enter a search query for the product you are using.

**Ex:** `http://0.0.0.0:8000/getProductInfo/rtx3070`

# Video
If you want to see a tiny demonstration of the project, you can visit the following link:

[Demo Video](https://youtu.be/02aoj_KxsIY)


## Pitfalls
### 1. Data Sourcing
As the challenge did not specify a requirement for where to source product data, I could have spent far longer researching and picking specific sources for my data but I ultimately went with Amazon just for the sheer number of products. In addition, I also had to implement way to search Amazon for the product name provided.

### 2. Scraping Data
Another challenge was with the complexity of scraping data. I only had a small amount of experience with data scraping from a past project I did involving tracking the price decrease of used Tesla vehicles sold in Vancouver. As Amazon has some protections in place to prevent scraping, I had the possibility of exploring premade solutions like ScraperAPI or developing my own via Python packages like BeautifulSoup. I ended up going with the latter, but I ended up spending a significant amount of my time exploring using GPT to parse the entirety of Amazon's HTML pages and extracting important features.

### 3. Python's quirks
Python is a great language but I do not have as much experience with it. I was grateful that it wasn't complicated to get started (and FastAPI was a blessing in that regard). However, I did notice that some of my time was eaten up getting caught up in some of Python's features that I wasn't completely knowledgeable of.

### 4. Time & Effort
I found it challenging to finish this project within the timeframe alloted. Given the number of features required for this project, it was difficult to balance spending time to rewrite and simplify the code when I had more to do. I sacrificed deploying the project due to these time constraints.


## Things I would do instead
If I had more time to work on this challenge, there are several things I would spend more time on:

1. **Search System**: I would spend more time making a better search system. Mine is currently limited by the fact that it returns the first element only, meaning that if two products have similar names (Like different editions of an RTX 4080 Graphics Card) it would choose the first that appeared in the list. I instead devoted time to ensuring the rest of the project did what was required, which prevented me from looking into ways to improve the search function.
2. **Different Product Datasets**: Instead of only using Amazon's system, I would instead scrape from multiple e-commerce sites, such as Ebay, different Shopify sites, and more. I did not attempt this as I figured it would be too costly timewise to work on implementing those features.
3. **Better Error Handling & Tests**: There is rudimentary error handling in the project, but with more time to approach and plan, I believe I could have made it much more robust. In addition, Test-Driven development is an important keystone of development today, but I neglected to use it here. In addition, I found I could not allocate the time to use the Logprobs feature of GPT, where I could have perhaps noted specific tokens GPT was unsure of and marked them to be supplemented with factual information taken from web scraping product information from other sites. In addition, I realized very late that large products could consume more tokens than the project would allow, so I would look for ways mitigate that issue.
4. **Performance Handling**: With more time, I could have investigated different LLMs and their performance with a task such as this. I only looked at GPT-4 and 3.5-turbo for this task, I found that GPT-4 provided more satisfactory output.