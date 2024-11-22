
## Preface

The project includes one `requriements.txt`, containing FastAPI and uvicorn, to run the webapp (webapp/main.py).

Use the command `pip install -r requriements.txt` to install the dependencies. 

Alternatively, virtual environments can be created using the command `python3 -m venv venv_py3`. Then perform `source venv_py3/bin/activate` to activate the local virtual environment.

## Instructions 

All the work are placed in `submission` folder.

1. `1_sql_query.sql` is the solution for first question.

2. Folder `2_round_robin` contains the solution the the 2nd question. It contains the following:
   - `db_schema.sql` for the DBSchema of the round robin design.
   - `design.md` is the high-level design.
   - `server.py` contains one server implemented using python and Flask. 

3. `3_minimum_deletions.py` is the solution to the 3rd question.
   
4. Folder `4_reward_system` contains the solution the the 4th question. It contains the following:
   - `db_schema.sql` for the DBSchema of the reward system design.
   - `UML_Dirgram.png` is the UML diagram of reward system. 
   - `reward_system.py` contains one functions code written in python.