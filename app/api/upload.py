from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
import os
import shutil
from datetime import datetime
import uuid

router = APIRouter()

# 允许的图片文件类型
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", 
    "image/webp", "image/bmp", "image/svg+xml"
}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传图片文件
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    # 验证文件大小
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail="图片大小不能超过 5MB"
            )
    
    # 重置文件指针
    await file.seek(0)
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{timestamp}_{current_user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    
    # 创建上传目录
    upload_dir = "uploads/images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 返回文件信息
    image_url = f"/uploads/images/{unique_filename}"
    
    return {
        "image_url": image_url,
        "image_name": file.filename,
        "file_size": file_size,
        "content_type": file.content_type
    }

@router.delete("/delete-image")
async def delete_image(
    image_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除图片文件
    """
    # 验证图片URL格式
    if not image_url.startswith("/uploads/images/"):
        raise HTTPException(
            status_code=400, 
            detail="无效的图片URL"
        )
    
    # 构建文件路径
    file_path = image_url.lstrip("/")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail="图片文件不存在"
        )
    
    # 删除文件
    try:
        os.remove(file_path)
        return {"message": "图片删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"图片删除失败: {str(e)}"
        )