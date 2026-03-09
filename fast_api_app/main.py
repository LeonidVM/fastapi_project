from fastapi import FastAPI

import validators
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import models, schemas, crud, keygen
from .database import SessionLocal, engine
from starlette.datastructures import URL
from .config import get_settings
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from fastapi.responses import Response
from sqlalchemy import func
import time

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)

def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

@app.get("/admin/analytics")
def get_simple_analytics(
        db: Session = Depends(get_db)
):
    total_urls = db.query(models.URL).count()
    active_urls = db.query(models.URL).filter(models.URL.is_active == True).count()
    total_clicks = db.query(func.sum(models.URL.clicks)).scalar() or 0

    top_urls = db.query(models.URL).filter(
        models.URL.is_active == True
    ).order_by(models.URL.clicks.desc()).limit(5).all()

    base_url = URL(get_settings().base_url)

    return {
        "total_urls": total_urls,
        "active_urls": active_urls,
        "total_clicks": total_clicks,
        "top_urls": [
            {
                "key": url.key,
                "url": str(base_url.replace(path=url.key)),
                "clicks": url.clicks,
                "target": url.target_url[:50] + "..." if len(url.target_url) > 50 else url.target_url
            }
            for url in top_urls
        ]
    }

@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    db_url = crud.create_db_url(db=db, url=url)

    crud.insert_creted_at(db=db, db_url=db_url)
    crud.insert_expires_at(db=db, db_url=db_url)

    return get_admin_info(db_url)

@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        expired_url = crud.get_db_url_by_key_admin(db=db, url_key=url_key)
        if expired_url and expired_url.expires_at <= datetime.utcnow():
            raise HTTPException(
                status_code=410,
                detail="К сожалению, ссылка устарела (5 минут), создайте новую"
            )
        else:
            raise_not_found(request)

@app.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLInfo,
)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)

@app.delete("/{url_key}")
def delete_url(
    url_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_key(db, url_key=url_key):
        message = f"Ссылка удалена '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)

@app.put("/url/{url_key}", response_model=schemas.URLInfo)
def update_url_key(
        url_key: str,
        url_update: schemas.URLUpdate,
        request: Request,
        db: Session = Depends(get_db)
):
    db_url = crud.get_db_url_by_key(db=db, url_key=url_key)
    if not db_url:
        raise_not_found(request)

    new_key = crud.create_unique_random_key(db=db)

    updated_url = crud.update_url_key(
        db=db,
        db_url=db_url,
        new_key=new_key
    )

    return get_admin_info(updated_url)

@app.get("/{url_key}/stats", response_model=schemas.URLStats)
def get_url_stats(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):

    if db_url := crud.get_db_url_by_key_admin(db=db, url_key=url_key):
        return schemas.URLStats(
            target_url=db_url.target_url,
            created_at=db_url.created_at,
            clicks=db_url.clicks,
            last_used=db_url.last_used,
            expires_at=db_url.expires_at,
            shortened_url=str(URL(get_settings().base_url).replace(path=db_url.key))
        )
    else:
        raise_not_found(request)

@app.get("/search/by-url")
def find_shortened_by_url(
        target_url: str,
        request: Request,
        db: Session = Depends(get_db)
):
    db_urls = db.query(models.URL).filter(
        models.URL.target_url == target_url
    ).all()

    if not db_urls:
        raise_not_found(request)

    base_url = URL(get_settings().base_url)

    results = []
    for db_url in db_urls:
        results.append({
            "key": db_url.key,
            "shortened_url": str(base_url.replace(path=db_url.key)),
            "target_url": db_url.target_url,
            "created_at": db_url.created_at,
            "expires_at": db_url.expires_at,
            "last_used": db_url.last_used,
            "clicks": db_url.clicks,
            "is_active": db_url.is_active,
            "admin_url": str(base_url.replace(
                path=app.url_path_for("administration info", secret_key=db_url.secret_key)
            )) if db_url.is_active else None
        })

    return {
        "query": target_url,
        "count": len(results),
        "results": results
    }

@app.post("/url/custom", response_model=schemas.URLCustomResponse)
def create_custom_url(
        url_data: schemas.URLCustomCreate,
        request: Request,
        db: Session = Depends(get_db)
):
    if not validators.url(url_data.target_url):
        raise_bad_request(message="Ссылка некорректная, попробуйте еще раз")

    if url_data.custom_key:
        custom_key = url_data.custom_key

        existing_url = crud.get_db_url_by_key(db=db, url_key=custom_key)
        if existing_url:
            raise HTTPException(
                status_code=400,
                detail=f"Ключ '{custom_key}' уже занят, попробуйте придумать другой"
            )
    else:
        custom_key = crud.create_db_url(db=db, url=url)

    secret_key = f"{custom_key}_{keygen.create_random_key(length=8)}"

    db_url = models.URL(
        target_url=url_data.target_url,
        key=custom_key,
        secret_key=secret_key,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow()+timedelta(minutes=5),
        is_active=True,
        clicks=0
    )

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    base_url = URL(get_settings().base_url)
    shortened_url = str(base_url.replace(path=db_url.key))
    admin_endpoint = app.url_path_for("administration info", secret_key=db_url.secret_key)
    admin_url = str(base_url.replace(path=admin_endpoint))

    return schemas.URLCustomResponse(
        message="Ура, ссылка создана!",
        key=db_url.key,
        custom_key=db_url.key,
        target_url=db_url.target_url,
        shortened_url=shortened_url,
        admin_url=admin_url,
        expires_at=db_url.expires_at,
    )

@app.get("/{url_key}/qrcode")
def generate_qrcode(
        url_key: str,
        db: Session = Depends(get_db)
):
    db_url = crud.get_db_url_by_key(db=db, url_key=url_key)
    if not db_url:
        raise_not_found(Request)

    base_url = URL(get_settings().base_url)
    short_url = str(base_url.replace(path=db_url.key))

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(short_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)

    return Response(
        content=img_bytes.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={url_key}_qrcode.png"}
    )



