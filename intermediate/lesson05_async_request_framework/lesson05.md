# 20211216

## Approach 1

Make 1 coroutine per async request that needs to be made
- Is hard to control rate limits across so many workers
- Large memory overhead
- If we are throttling, then only N coroutines are allowed to run at a time
  - No point creating thousands if we are only running N at a time
  
## Approach 2

Make 1 couroutine per "rate limited worker"
- Can use number of workers == number of items allowed in rate limit period
- Can make specialised workers for cases like pagination
- Can use a queue to control rate limiting/pausing across async coroutines
  - i.e. if one coroutine receives a 503, stop ALL coroutines for N period