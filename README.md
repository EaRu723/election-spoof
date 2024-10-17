## run code
$ cd backend
$ uvicorn app:app --reload

## Debug ERROR:    [Errno 48] Address already in use
$ lsof -i :8000
$ kill -9 <PID>