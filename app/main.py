import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import MongoDB
from config.development import config
from model.student import createStudentModel, updateStudentModel


mongo_config = config["mongo_config"]

mongo_db = MongoDB(  # import MongoDB จาก mongodb.py
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()  # เชื่อมกับ mongodb

app = FastAPI()

app.add_middleware(  # middleare เหมือนตัวคั่นกลาง เป็นส่วนนึงของ api
    CORSMiddleware,
    allow_origins=["*"],  # * คือ ทุกคนสามารถเข้าถึงได้หมด
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return JSONResponse(content={"message": "Student Info"}, status_code=200)


@app.get("/students/")
def get_students(
    sort_by: Optional[str] = None,  # Optional ถ้าไม่เป็น str ก็ให้เป็น none
    order: Optional[str] = Query(
        None, min_length=3, max_length=4
    ),  # อย่างน้อยต้องมี3 ไม่เกิน 4
):

    try:
        result = mongo_db.find(sort_by, order)  # เรียกใช้ func find จาก mongodb.py
    except:  # ถ้ามีปัญหา
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )

    # api return [] -> mongo ยังไม่มี
    # insert doc mongo
    # api return ของใน mongo ออกมา


@app.get("/students/{student_id}")
def get_students_by_id(
    student_id: str = Path(None, min_length=10, max_length=10)
):  # ไม่น้อยกว่า 10 ตัวและไม่เกิน 10 ตัว
    try:
        result = mongo_db.find_one(student_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="Student Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/students")
def create_books(student: createStudentModel):  # รับ createstudentmodel จากการ import
    try:
        student_id = mongo_db.create(student)  # เรียกใช้ method create
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": student_id,
            },
        },
        status_code=201,
    )


@app.patch("/students/{student_id}")
def update_books(
    student: updateStudentModel,
    student_id: str = Path(None, min_length=10, max_length=10),
):
    print("student", student)
    try:
        updated_student_id, modified_count = mongo_db.update(student_id, student)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Student Id: {updated_student_id} is not update want fields",
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": updated_student_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/students/{student_id}")
def delete_book_by_id(student_id: str = Path(None, min_length=10, max_length=10)):
    try:
        deleted_student_id, deleted_count = mongo_db.delete(student_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Student Id: {deleted_student_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "student_id": deleted_student_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001, reload=True)
