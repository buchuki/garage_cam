Weekend project to get notified when I leave my garage door open. Uses machine learning (support vector machines, specifically) trained on images from a security camera that were uploaded to an FTP server.

See [my blog post](https://dusty.phillips.codes/2018/08/15/computer-vision-in-three-lines-of-code-plus-a-bunch-more-lines/) for a detailed tutorial on how this all works.

Requires a `config.py` in the source directory that looks something like this:


```python
ftp = {"host": "<host_ip>", "username": "<user>", "password": "<secret>"}
ifttt_key = "<key>"
open_warning_seconds = 3600 # one hour
twilio = {
    "account": "<account number>",
    "token": "<secret>",
    "from": "+<my twilio line>",
    "to": "+<my personal phone number",
}
```
