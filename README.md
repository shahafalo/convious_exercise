# Convious Exercise

by Shahaf Alon

This is a small scale (but easily sclable) API service for managing the hardest question of all:
"Where should we eat today? let's vote!"


## Notes about the exercise

Due to the fact that this is an exerecise I had to decide what is crucial and what can be done later (if it were a real project) and make a few compromises, these are a few of them:

### Use SQLite Instead of PostgreSQL:

SQLite is a lightweight database system that is well-suited for smaller applications.
By choosing SQLite over PostgreSQL, I opted for simplicity and ease of setup.
In a real project I would have started with PostgreSQL, because of its is advanced features, scalability, and performance.

### Only Basic Input Validations:

Implementing extensive input validations can be time-consuming so I chose to focus on the most critical ones.
While FastAPI offers great type validations I would have added user authentication and more extensive data validations.

### Leave an Open Issue with Recalculation of Scores After Deleting and Updating Votes on Previous Days' Votes:

By changing past votes we might change some of the winners. E.g. we can remove all of the votes that the winner last week received, and therefore any winner calculation for that day from now on, will present a false winner.
There are a few good possible ways to address this issue, further team discussion and product understanding is needed to decide on the right solution.


Those are a few points that I would have implemented if it were a real project:

### Change ID to BIGINT if Needed While Moving to PostgreSQL:

This step is essential to ensure that the IDs can accommodate growing data volumes without the risk of reaching their maximum value and causing issues with data integrity.

### More Input Validations:

This can include checking for additional valid data formats, proper data lengths.

### Add User Authentication and User Validation for Votes:

Introduce a user authentication system to allow only registered and authenticated users to participate in voting. Implement user validation for votes to prevent unauthorized or fraudulent voting. User validation may involve verifying user identity through email verification or other methods.

### Do Bulk Updates and Deletions:

Optimize the application's performance by implementing bulk updates and deletions when handling large datasets. Bulk operations are more efficient than processing individual records one by one. I would have used PostgreSQL's capabilities for bulk updates and deletions to streamline these operations.

### Add Further Testing:

Additional deep dive testing is needed on some of the features. All of the features have been tested on the live enviorment, but this isn't a replacment for unit tests.


## Installation

```
git clone https://github.com/shahafalo/convious_exercise.git
cd convious_exercise
pip install -r requirements.txt
```

## Usage

Run the script with `uvicorn main:app`.  

## Tests

Run the tests with `pytest src/`.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python 3.7+

## Usage Flow Example:

create restaurant(s) -> create voter(s) -> create vote(s) -> get winner (return value is restaurant id) -> read restaurant by id
