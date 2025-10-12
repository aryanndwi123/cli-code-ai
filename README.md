python3 -m venv venv                  
source venv/bin/activate
venv\Scripts\activate
pip install -r requirements.txt

lsof -i:5000
kill -9 4744