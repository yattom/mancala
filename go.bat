python -m mancala.learner record 100 m100.db
python -m mancala.learner record 200 m200.db
python -m mancala.learner record 300 m300.db
python -m mancala.learner record 400 m400.db
python -m mancala.learner record 500 m500.db
python -m mancala.learner record 600 m600.db
python -m mancala.learner record 700 m700.db
python -m mancala.learner record 800 m800.db
python -m mancala.learner record 900 m900.db

python -m mancala.learner match 100 m100.db
python -m mancala.learner match 100 m200.db
python -m mancala.learner match 100 m300.db
python -m mancala.learner match 100 m400.db
python -m mancala.learner match 100 m500.db
python -m mancala.learner match 100 m600.db
python -m mancala.learner match 100 m700.db
python -m mancala.learner match 100 m800.db
python -m mancala.learner match 100 m900.db

python -m mancala.learner record 1000 m1000.db > nul
python -m mancala.learner match 100 m1000.db

python -m mancala.learner record 10000 m10000.db > nul
python -m mancala.learner match 100 m10000.db

