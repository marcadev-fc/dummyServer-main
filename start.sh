export FLASK_APP=app
export FLASK_ENV=development
export FLASK_DEBUG=1
export DD_SERVICE="dummy-server" 
export DD_ENV="prod" 
export DD_LOGS_INJECTION=true 
export DD_PROFILING_ENABLED=true
pipenv run ddtrace-run flask run --host=0.0.0.0 --port=80