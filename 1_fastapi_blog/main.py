from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from models import User, Post

from database import engine , get_db , Base
from schemas import PostCreate, PostResponse , UserCreate , UserResponse, PostUpdate , UserUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


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



# ------------ Templates routes  -------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False, name="home")
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False, name="posts")
def home(request: Request , db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(request, "home.html", {"posts": posts})


@app.get("/post/{post_id}", include_in_schema=False, name="post_page")
def post_page(request: Request, post_id: int , db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()

    if post:
        title  = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )

    return templates.TemplateResponse(request, "error.html")


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(request: Request, user_id: int , db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    result = db.execute(select(Post).where(Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )    




# ------------ User Apis  -------------------------------------
@app.post("/api/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def user_create(user: UserCreate , db : Annotated[Session, Depends(get_db)]):
    
    result = db.execute(
        select(User).where(User.username==user.username)
    )

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    
    

    result = db.execute(
        select(User).where(User.email==user.email)
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Email  already exist"
        )
    

    new_user = User(
        username = user.username,
        email = user.email
    )

    db.add(new_user)  # stage changes
    db.commit()       # execute and save changes 
    db.refresh(new_user)  # refresh db 

    return new_user



@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(User).where(User.id == user_id),
    )
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int,user_data:UserUpdate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(User).where(User.id == user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    if user_data.username is not None and user_data.username !=user.username:
        result = db.execute(
        select(User).where(User.username==user_data.username)
    )

        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="Username already exist"
            )
    
    

    if user_data.email is not None and user_data.email !=user.email:
        result = db.execute(
            select(User).where(User.email==user_data.email)
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="Email  already exist"
            )
        
    update_user_data = user_data.model_dump(exclude_unset=True)    
    for field , value in update_user_data.items():
        setattr(user,field,value)


    db.commit()
    db.refresh(user)

    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(User).where(User.id == user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    db.delete(user)
    db.commit()



# ------------ Post Apis -------------------------------------
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(Post).where(Post.user_id == user_id))
    posts = result.scalars().all()
    return posts



@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int , db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    
    if post:
        return post

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found")


@app.post(
    "/api/posts/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(User).where(User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post))
    posts = result.scalars().all()
    return posts


@app.put("/api/post/{post_id}", response_model=PostResponse)
def update_post_put(post_id: int ,post_data:PostCreate, db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found")
        
    if post.user_id != post_data.user_id: 
        result = db.execute(select(User).where(User.id == post_data.user_id))
        user = result.scalars().first()
        
        if not  user:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
    post.title = post_data.title    
    post.content = post_data.content    
    post.user_id = post_data.user_id    

    db.commit()
    db.refresh(post)
    
    return post

    

@app.patch("/api/post/{post_id}", response_model=PostResponse)
def update_post_patch(post_id: int ,post_data:PostUpdate, db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found")
        

    update_data = post_data.model_dump(exclude_unset=True)    

    for field , value in update_data.items():
        setattr(post,field, value)
    
    db.commit()
    db.refresh(post)

    return post


@app.delete("/api/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int , db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found")
    
    db.delete(post)
    db.commit()
    
        





#  general http and validation error handler (fastapi is built over starlette)
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if exc.detail else "An error occured"

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": message},
        )

    return templates.TemplateResponse(request, "error.html", {"status_code": exc.status_code, "message": message}, status_code=exc.status_code)


# for validation error handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
