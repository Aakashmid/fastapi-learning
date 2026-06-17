from fastapi import FastAPI , Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.mount("/static",StaticFiles(directory="static"),name="static")

templates =  Jinja2Templates(directory="templates")


posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

# can make two routes point to the same api 
#  includce_in_schmea  false means it will not show up in the docs


@app.get("/",response_class = HTMLResponse , include_in_schema = False , name="home")
@app.get("/posts",response_class = HTMLResponse , include_in_schema=False , name="posts")  
def home(request: Request ):
    return templates.TemplateResponse(request,"home.html",{"posts":posts})




@app.get("/api/posts")
def get_posts():
    return  posts