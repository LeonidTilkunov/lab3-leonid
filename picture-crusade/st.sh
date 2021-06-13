gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
sleep 25
APP_CODE=$?
sleep 5
echo $APP_PID 
kill -TERM $APP_PID
echo app code $APP_CODE
exit $APP_CODE
