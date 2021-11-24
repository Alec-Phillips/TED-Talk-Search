# TED-Talk-Search - Alec Phillips, Yash Karandikar

## To Run:
- Clone Repo
- Download pre-training data: https://drive.google.com/file/d/1XVtOtZFivdPw1edEhQwb-uFI2y4WcrOz/view?usp=sharing and place into the same directory as the code files
  - This is a very large file (~350 MB), so it was too large to push to GitHub
- Run main.py

## Design:
- During training, each Ted Talk transcript was converted into a vector using TF-IDF and finding the centroid vector for each document
  - This is the data stored in the google drive file (training the model takes a long time, so we saved the pre-training data in json format so that it can be read in instead of generated each time)
- When the user enters a query, the same process is applied to get a vector representation for the query
- The query vector is then compared with each document vector using cosine similarity, and the best matches are returned

## Constraints:
- The TF-IDF process squashes the importance of terms that appear more often, so queries for certain terms that occur throughout a very large number of the talks end up being uninformative and don't return helpful results
  - For instance, the vector for a query for 'culture' will just be represented by all 0's, because climate appears so frequently in the different Ted Talks
  - Because of this, the cosine similarity will get the same result when comparing this query to each document
- To address this issue, we implemented a secondary search strategy that uses the 'topics' column of the dataset:
  - In the case that the query is too general, we use dependency parsing to determine the nominative subject (or just root, if there is no subject), and we search through the 'topics' list for matching talks
  - We then sort the matches by the number of views that the talk has had, and return the top ten results
- This solution worked fairly well, but it only works for terms that actually appear in the 'topics' column, which is a fairly small set of terms
- If we were to continue developing this, we would definitely focus on finding a more robust solution to this issue
