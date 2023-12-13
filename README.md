# To run the code on the VM:
cd daldric1/project

sudo docker-compose up --build

sudo docker exec -ti project_chan_crawler_1 /bin/bash

# To begin the crawler:
python init_chan.py

# To recheck toxicity on ModerateHatespeech for the rows that have not been checked:
python check_toxic_retry.py

exit

sudo docker exec -ti project_reddit_crawler_1 /bin/bash

# To begin the crawler:
python init_reddit.py

# To recheck toxicity on ModerateHatespeech for the rows that have not been checked:
python check_toxic_retry.py

exit

# To run the dashboard:
sudo docker exec -ti project_dash-app_1 /bin/bash

python not_flask.py

Should get message: Dash is running on http://0.0.0.0:80/

Have been able to see the dashboard on http://localhost:59164/

^C followed by exit

# To see the database:
sudo docker exec -ti project_postgres_1 /bin/bash

psql -U postgres

# To access the chan database:
\c chan_crawler

can access the posts table

# To access the init_reddit database:
\c reddit_crawler

can access the posts and comments table

exit
exit

# To stop the crawlers and faktory:
sudo docker compose down

“We have done this assignment completely on our own. We have not copied it, nor have we given my solution to anyone else. We understand that if we are involved in plagiarism or cheating we will have to sign an official form that we have cheated and that this form will be stored in my official university record. We also understand that we will receive a grade of 0 for the involved assignment and our grade will be reduced by one level (e.g., from A to B) for my our offense, and that we will receive a grade of “F” for the course for any additional offense of any kind.”

Distribution of work:

Developing code: everybody

Creating visuals: everybody

Writing report: everybody
