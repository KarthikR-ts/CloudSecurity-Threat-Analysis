
import os
import pyarrow.parquet as pq
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import require_role
from typing import List, Dict, Any

router = APIRouter()

from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def get_parquet_path(filename: str):
    # Security: Ensure filename is just a basename, no path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")
    
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return path

@router.get("/datasets", dependencies=[Depends(require_role("ml_researcher"))])
def list_datasets():
    """List available parquet files in the data directory."""
    try:
        if not os.path.exists(DATA_DIR):
            return {"datasets": []}
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".parquet")]
        return {"datasets": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema", dependencies=[Depends(require_role("ml_researcher"))])
def get_schema(filename: str = Query(..., description="Filename e.g. train_ml_ready.parquet")):
    path = get_parquet_path(filename)
    try:
        # Read metadata only, not the file content
        parquet_file = pq.ParquetFile(path)
        schema = parquet_file.schema
        
        # Convert schema to JSON-friendly format
        fields = []
        for name in schema.names:
            field = schema.field(name)
            fields.append({
                "name": name,
                "type": str(field.type),
                "nullable": field.nullable
            })
            
        return {"filename": filename, "schema": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading schema: {str(e)}")

@router.get("/stats", dependencies=[Depends(require_role("ml_researcher"))])
def get_stats(filename: str = Query(...)):
    path = get_parquet_path(filename)
    try:
        parquet_file = pq.ParquetFile(path)
        metadata = parquet_file.metadata
        return {
            "filename": filename,
            "num_rows": metadata.num_rows,
            "num_columns": metadata.num_columns,
            "serialized_size": metadata.serialized_size,
            "num_row_groups": metadata.num_row_groups
        }
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error reading stats: {str(e)}")

@router.get("/sample", dependencies=[Depends(require_role("ml_researcher"))])
def get_sample(filename: str = Query(...), limit: int = 10):
    path = get_parquet_path(filename)
    try:
        # Read only a small subset of rows
        table = pq.read_table(path)
        # Slicing is cheap on Arrow tables? 
        # Actually proper way to not read all is complex with read_table if we want exact row skipping
        # But 'read_table' reads everything into memory usually?
        # BETTER: parquet_file.read_row_group(0) if limit is small?
        
        pf = pq.ParquetFile(path)
        # Read first row group (usually enough for sample)
        # If files are huge, this is safer than read_table(path)
        first_group = pf.read_row_group(0) 
        
        # Slice the table
        slice_table = first_group.slice(0, min(limit, first_group.num_rows))
        
        # Convert to dictionary
        return {"data": slice_table.to_pylist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading sample: {str(e)}")
